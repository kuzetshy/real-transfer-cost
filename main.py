from datetime import datetime
from typing import List
from fastapi import FastAPI, Query, HTTPException

from rates_client import RatesClient
from calculator import WiseProvider, RevolutProvider, CzechBankProvider, ProviderQuote

app = FastAPI(
    title="Real Transfer Cost API",
    description="API for comparing real transfer costs between different providers (Wise, Revolut, Czech Bank) based on mid-market rates.",
    version="0.1.0"
)

rates_client = RatesClient()

# Register our providers
providers = [
    WiseProvider(),
    RevolutProvider(),
    CzechBankProvider()
]

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Real Transfer Cost API is running!"
    }

@app.get("/api/v1/rates")
async def get_current_rate(
    from_currency: str = Query("CZK", description="Original currency, e.g., CZK"),
    to_currency: str = Query("EUR", description="Target currency, e.g., EUR")
):
    rate = await rates_client.get_rate(from_currency, to_currency)
    return {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "mid_market_rate": rate
    }

@app.get("/api/v1/compare", response_model=List[ProviderQuote])
async def compare_transfers(
    amount: float = Query(10000.0, gt=0, description="Transfer amount"),
    from_currency: str = Query("CZK", description="Sending currency"),
    to_currency: str = Query("EUR", description="Receiving currency")
):
    # 1. Получаем чистый курс с внешнего API
    mid_rate = await rates_client.get_rate(from_currency, to_currency)
    
    # 2. Проверяем, выходной ли сегодня день (суббота=5, воскресенье=6)
    is_weekend = datetime.now().weekday() >= 5

    # 3. Считаем предложения от всех провайдеров
    results = [
        provider.calculate(amount=amount, mid_rate=mid_rate, is_weekend=is_weekend)
        for provider in providers
    ]

    # 4. Сортируем: сверху тот, кто доставит больше всего денег получателю!
    results.sort(key=lambda x: x.received_amount, reverse=True)

    return results