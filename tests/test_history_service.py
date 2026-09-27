import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from app.db.models import ExchangeRateHistory
from app.services.history import HistoryService

@pytest.mark.asyncio
async def test_upsert_rates_batch_insert_and_update(db_session):
    service = HistoryService(db_session)
    test_date = date(2001, 5, 10)  # Дата из прошлого

    initial_records = [
        {
            "base_currency": "EUR",
            "target_currency": "CZK",
            "rate": Decimal("25.100000"),
            "rate_date": test_date,
            "provider": "frankfurter",
        },
        {
            "base_currency": "USD",
            "target_currency": "CZK",
            "rate": Decimal("23.200000"),
            "rate_date": test_date,
            "provider": "frankfurter",
        },
    ]

    inserted_count = await service.upsert_rates_batch(initial_records)
    assert inserted_count == 2

    # Upsert с новым значением
    updated_records = [
        {
            "base_currency": "EUR",
            "target_currency": "CZK",
            "rate": Decimal("25.999999"),
            "rate_date": test_date,
            "provider": "frankfurter",
        }
    ]
    await service.upsert_rates_batch(updated_records)
    db_session.expire_all()

    stmt = select(ExchangeRateHistory).where(
        ExchangeRateHistory.rate_date == test_date,
        ExchangeRateHistory.base_currency == "EUR",
    )
    record = (await db_session.scalars(stmt)).first()
    assert record is not None
    assert record.rate == Decimal("25.999999")