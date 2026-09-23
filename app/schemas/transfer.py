from pydantic import BaseModel

class ProviderQuote(BaseModel):
    provider_name: str
    sent_amount: float
    received_amount: float
    total_fee_czk: float
    effective_rate: float
    markup_loss_czk: float
    description: str
    