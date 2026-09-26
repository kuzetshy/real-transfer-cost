# app/schemas/quotes.py
from decimal import Decimal
from pydantic import BaseModel, Field

class QuoteRequest(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3, example="EUR")
    to_currency: str = Field(..., min_length=3, max_length=3, example="CZK")
    amount: Decimal = Field(..., gt=0, example=1000.0)

class ProviderQuote(BaseModel):
    provider_name: str
    transfer_fee: Decimal
    exchange_rate: Decimal
    recipient_gets: Decimal
    total_cost: Decimal  # Разница между идеальным mid-market получением и фактическим 💡
    is_best: bool = False

class QuoteCompareResponse(BaseModel):
    base_currency: str
    target_currency: str
    amount: Decimal
    mid_market_rate: Decimal
    quotes: list[ProviderQuote]