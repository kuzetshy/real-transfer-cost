from datetime import datetime
from typing import List
from fastapi import APIRouter, Query

from app.schemas.transfer import ProviderQuote
from app.services.rates import RatesClient
from app.services.calculator import WiseProvider, RevolutProvider, CzechBankProvider

router = APIRouter(prefix="/v1", tags=["Transfer Calculation"])

rates_client = RatesClient()
providers = [
    WiseProvider(),
    RevolutProvider(),
    CzechBankProvider()
]

@router.get("/rates")
async def get_current_rate(
    from_currency: str = Query("CZK", description="Исходная валюта"),
    to_currency: str = Query("EUR", description="Целевая валюта")
):
    rate = await rates_client.get_rate(from_currency, to_currency)
    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "mid_market_rate": rate
    }

@router.get("/compare", response_model=List[ProviderQuote])
async def compare_transfers(
    amount: float = Query(10000.0, gt=0, description="Сумма перевода"),
    from_currency: str = Query("CZK", description="Валюта отправки"),
    to_currency: str = Query("EUR", description="Валюта получения")
):
    mid_rate = await rates_client.get_rate(from_currency, to_currency)
    is_weekend = datetime.now().weekday() >= 5

    results = [
        provider.calculate(amount=amount, mid_rate=mid_rate, is_weekend=is_weekend)
        for provider in providers
    ]
    results.sort(key=lambda x: x.received_amount, reverse=True)
    return results
