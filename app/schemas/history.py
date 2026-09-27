from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field

class RateHistoryPoint(BaseModel):
    date: date
    rate: Decimal = Field(..., description="Exchange rate on that date")

class RateHistoryResponse(BaseModel):
    base_currency: str
    target_currency: str
    provider: str
    points_count: int
    history: list[RateHistoryPoint]