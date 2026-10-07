from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import ExchangeRateHistory


class HistoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_rates_batch(
        self,
        rates_data: list[dict],
    ) -> int:
        """
        Bulk insert or update exchange rate entries.
        Each rates_data dictionary schema:
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

        # Update exchange rate if an entry for the pair, date, and provider already exists
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
        Retrieve exchange rate history for a specified date range,
        sorted in ascending order by date (optimized for charts).
        """
        # Default to the last 30 days if both boundary dates are omitted
        if not to_date and not from_date:
            to_date = date.today()
            from_date = to_date - timedelta(days=30)
        elif not to_date and from_date:
            to_date = date.today()
        elif not from_date and to_date:
            from_date = to_date - timedelta(days=30)

        stmt = (
            select(ExchangeRateHistory)
            .where(
                ExchangeRateHistory.base_currency == base_currency.upper(),
                ExchangeRateHistory.target_currency == target_currency.upper(),
                ExchangeRateHistory.rate_date >= from_date,
                ExchangeRateHistory.rate_date <= to_date,
            )
            .order_by(ExchangeRateHistory.rate_date.asc())
        )

        result = await self.session.scalars(stmt)
        return list(result.all())

    