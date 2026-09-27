import asyncio
from datetime import date, timedelta
from app.db.session import async_session_maker
from app.services.rates import RatesClient
from app.services.history import HistoryService

async def seed_last_days(days: int = 30):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    print(f"🔄 Сбор истории курсов с {start_date} по {end_date}...")

    rates_client = RatesClient()
    
    # Пары, которые нам нужны для калькулятора
    tasks_config = [
        {"base": "EUR", "targets": ["CZK"]},
        {"base": "USD", "targets": ["CZK"]},
        {"base": "CZK", "targets": ["EUR", "USD"]},
    ]

    records_to_insert = []

    for cfg in tasks_config:
        base = cfg["base"]
        targets = cfg["targets"]
        print(f"📊 Запрос {base} -> {targets}...")

        try:
            rates_by_date = await rates_client.get_historical_rates(
                base=base,
                symbols=targets,
                start_date=start_date,
                end_date=end_date,
            )

            for rate_date, target_map in rates_by_date.items():
                for target_curr, rate_val in target_map.items():
                    records_to_insert.append({
                        "base_currency": base,
                        "target_currency": target_curr,
                        "rate": rate_val,
                        "rate_date": rate_date,
                        "provider": "frankfurter",
                    })
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке {base} -> {targets}: {e}")

    print(f"📥 Всего собрано {len(records_to_insert)} записей. Сохранение в PostgreSQL...")

    async with async_session_maker() as session:
        service = HistoryService(session)
        count = await service.upsert_rates_batch(records_to_insert)
        print(f"✅ Успешно сохранено/обновлено {count} записей в БД!")

if __name__ == "__main__":
    asyncio.run(seed_last_days(30))
    