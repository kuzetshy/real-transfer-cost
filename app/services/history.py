from datetime import date
from decimal import Decimal
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ExchangeRateHistory
from sqlalchemy import select 


class HistoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_rates_batch(
        self,
        rates_data: list[dict],
    ) -> int:
        """
        Массовая вставка или обновление записей курсов.
        Каждый элемент rates_data:
        {
            "base_currency": "EUR",
            "target_currency": "CZK",
            "rate": Decimal("25.1234"),
            "rate_date": date(2026, 8, 28),
            "provider": "frankfurter"
        }
        """
        if not rates_data:
            return 0

        stmt = insert(ExchangeRateHistory).values(rates_data)
        
        # Если запись для пары, даты и провайдера уже есть — обновляем курс
        stmt = stmt.on_conflict_do_update(
            constraint="uq_rate_history_pair_date_provider",
            set_={"rate": stmt.excluded.rate},
        )

        await self.session.execute(stmt)
        await self.session.commit()
        return len(rates_data)



    async def get_history(
        self,
        base_currency: str,
        target_currency: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExchangeRateHistory]:
        """
        Возвращает историю курсов, отсортированную по возрастанию даты (для графиков).
        """
        stmt = (
            select(ExchangeRateHistory)
            .where(
                ExchangeRateHistory.base_currency == base_currency.upper(),
                ExchangeRateHistory.target_currency == target_currency.upper(),
            )
            .order_by(ExchangeRateHistory.rate_date.asc())
        )

        if from_date:
            stmt = stmt.where(ExchangeRateHistory.rate_date >= from_date)
        if to_date:
            stmt = stmt.where(ExchangeRateHistory.rate_date <= to_date)

        result = await self.session.scalars(stmt)
        return list(result.all())
    