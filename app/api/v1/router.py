from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.transfer import ProviderQuote
from app.schemas.history import RateHistoryResponse, RateHistoryPoint
from app.services.rates import rates_client  
from app.services.calculator import WiseProvider, RevolutProvider, CzechBankProvider
from app.services.history import HistoryService


router = APIRouter(tags=["Transfer Calculation & Rates"])

# Registered transfer provider calculation strategies
providers = [
    WiseProvider(),
    RevolutProvider(),
    CzechBankProvider()
]


@router.get("/rates")
async def get_current_rate(
    from_currency: str = Query("CZK", description="Source currency code", min_length=3, max_length=3),
    to_currency: str = Query("EUR", description="Target currency code", min_length=3, max_length=3)
):
    """Fetch current mid-market exchange rate between two currencies."""
    rate = await rates_client.get_rate(from_currency, to_currency)
    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "mid_market_rate": rate
    }


@router.get("/compare", response_model=List[ProviderQuote])
async def compare_transfers(
    amount: Decimal = Query(Decimal("10000.0"), gt=0, description="Transfer amount"),
    from_currency: str = Query("CZK", description="Source currency code", min_length=3, max_length=3),
    to_currency: str = Query("EUR", description="Target currency code", min_length=3, max_length=3)
):
    """Compare transfer fees, effective exchange rates, and received amounts across providers."""
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
    base: str = Query("EUR", description="Base currency code", min_length=3, max_length=3),
    target: str = Query("CZK", description="Target currency code", min_length=3, max_length=3),
    days: int = Query(default=30, ge=1, le=365, description="Timeframe in days (used when from_date is omitted)"),
    from_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical exchange rate data points within a specified time range."""
    base_curr = base.upper()
    target_curr = target.upper()

    if base_curr == target_curr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Base and target currencies must not be identical."
        )

    end = to_date or date.today()
    start = from_date or (end - timedelta(days=days))

    if start > end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date (from_date) cannot be later than end date (to_date)."
        )

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