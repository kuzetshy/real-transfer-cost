from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.transfer import ProviderQuote
from app.schemas.history import RateHistoryResponse, RateHistoryPoint
from app.services.rates import rates_client  
from app.services.calculator import WiseProvider, RevolutProvider, CzechBankProvider
from app.services.history import HistoryService


router = APIRouter(tags=["Transfer Calculation & Rates"])

providers = [
    WiseProvider(),
    RevolutProvider(),
    CzechBankProvider()
]


@router.get("/rates")
async def get_current_rate(
    from_currency: str = Query("CZK", description="Исходная валюта", min_length=3, max_length=3),
    to_currency: str = Query("EUR", description="Целевая валюта", min_length=3, max_length=3)
):
    rate = await rates_client.get_rate(from_currency, to_currency)
    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "mid_market_rate": rate
    }


@router.get("/compare", response_model=List[ProviderQuote])
async def compare_transfers(
    amount: Decimal = Query(Decimal("10000.0"), gt=0, description="Сумма перевода"),
    from_currency: str = Query("CZK", description="Валюта отправки", min_length=3, max_length=3),
    to_currency: str = Query("EUR", description="Валюта получения", min_length=3, max_length=3)
):
    mid_rate = await rates_client.get_rate(from_currency, to_currency)
    is_weekend = datetime.now().weekday() >= 5

    results = [
        provider.calculate(amount=amount, mid_rate=mid_rate, is_weekend=is_weekend)
        for provider in providers
    ]
    results.sort(key=lambda x: x.received_amount, reverse=True)
    return results


@router.get("/rates/history", response_model=RateHistoryResponse)
async def get_rates_history(
    base: str = Query("EUR", description="Базовая валюта", min_length=3, max_length=3),
    target: str = Query("CZK", description="Целевая валюта", min_length=3, max_length=3),
    days: int = Query(default=30, ge=1, le=365, description="Период в днях (используется, если from_date не задан)"),
    from_date: date | None = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    base_curr = base.upper()
    target_curr = target.upper()

    if base_curr == target_curr:
        raise HTTPException(
            status_code=400,
            detail="Базовая и целевая валюты не должны совпадать."
        )

    end = to_date or date.today()
    start = from_date or (end - timedelta(days=days))

    history_service = HistoryService(db)
    records = await history_service.get_history(
        base_currency=base_curr,
        target_currency=target_curr,
        from_date=start,
        to_date=end,
    )

    history_points = [
        RateHistoryPoint(date=r.rate_date, rate=r.rate)
        for r in records
    ]

    return RateHistoryResponse(
        base_currency=base_curr,
        target_currency=target_curr,
        provider="frankfurter",
        points_count=len(history_points),
        history=history_points,
    )
