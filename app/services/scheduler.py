import logging
from datetime import datetime, date
from decimal import Decimal
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.session import async_session_maker
from app.services.rates import rates_client
from app.services.calculator import WiseProvider, RevolutProvider, CzechBankProvider
from app.services.history import HistoryService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Список провайдеров для расчёта эффективного курса
providers = [
    WiseProvider(),
    RevolutProvider(),
    CzechBankProvider(),
]

SUPPORTED_PAIRS = [
    ("EUR", "CZK"),
    ("CZK", "EUR"),
    ("USD", "CZK"),
    ("CZK", "USD"),
]


async def collect_daily_rates_job():
    """
    Фоновая задача: собирает mid-market курс и эффективные курсы провайдеров,
    сохраняя их в историю через HistoryService пачкой (batch upsert).
    """
    logger.info("🕒 [Scheduler] Starting daily exchange rates collection...")
    today = date.today()
    is_weekend = datetime.now().weekday() >= 5
    base_amount = Decimal("1000.0")

    records_to_insert = []

    for from_curr, to_curr in SUPPORTED_PAIRS:
        try:
            # 1. Получаем среднерыночный курс (Frankfurter/ECB)
            mid_rate = await rates_client.get_rate(from_curr, to_curr)

            records_to_insert.append({
                "base_currency": from_curr.upper(),
                "target_currency": to_curr.upper(),
                "rate": mid_rate,
                "rate_date": today,
                "provider": "frankfurter",
            })

            # 2. Прогоняем через калькуляторы провайдеров
            for provider in providers:
                quote = provider.calculate(
                    amount=base_amount,
                    mid_rate=mid_rate,
                    is_weekend=is_weekend,
                )
                rate_value = getattr(quote, "rate", None) or getattr(quote, "effective_rate", mid_rate)
                provider_name = getattr(
                    quote, 
                    "provider_name", 
                    provider.__class__.__name__.replace("Provider", "").lower()
                )

                records_to_insert.append({
                    "base_currency": from_curr.upper(),
                    "target_currency": to_curr.upper(),
                    "rate": rate_value,
                    "rate_date": today,
                    "provider": provider_name.lower(),
                })

            logger.info(f"✅ Prepared rates for pair {from_curr} -> {to_curr}")

        except Exception as pair_err:
            logger.error(
                f"❌ Failed to collect rates for {from_curr} -> {to_curr}: {pair_err}",
                exc_info=True,
            )

    if not records_to_insert:
        logger.warning("⚠️ [Scheduler] No records collected. Skipping DB upsert.")
        return

    try:
        async with async_session_maker() as session:
            history_service = HistoryService(session)
            saved_count = await history_service.upsert_rates_batch(records_to_insert)
            logger.info(f"🎉 [Scheduler] Saved {saved_count} rates into DB.")
    except Exception as db_err:
        logger.error(f"💥 [Scheduler] Database error during upsert: {db_err}", exc_info=True)


def start_scheduler():
    """Запуск шедулера по расписанию в 14:30 (Europe/Prague)."""
    scheduler.add_job(
        collect_daily_rates_job,
        trigger="cron",
        hour=14,
        minute=30,
        timezone="Europe/Prague",
        id="daily_rates_collector",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("🚀 [Scheduler] APScheduler started.")


def stop_scheduler():
    """Корректная остановка шедулера."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("🛑 [Scheduler] APScheduler stopped.")

        