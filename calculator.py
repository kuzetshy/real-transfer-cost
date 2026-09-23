from abc import ABC, abstractmethod
from datetime import datetime
from pydantic import BaseModel

# unite structure for responses from each service
class ProviderQuote(BaseModel):
    provider_name: str
    sent_amount: float
    received_amount: float
    total_fee_czk: float
    effective_rate: float
    markup_loss_czk: float  # hidden loss due to worse exchange rate
    description: str

# Basic abstract class for all providers
class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        pass

# 1. strategy: Wise
class WiseProvider(BaseProvider):
    def __init__(self):
        super().__init__("Wise")
        self.percent_fee = 0.0045  # 0.45%
        self.fixed_fee_czk = 15.0  # 15 CZK

    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        # Wise takes comission: 0.45% of the amount + 15 CZK fixed fee
        fee = (amount * self.percent_fee) + self.fixed_fee_czk
        convertible_amount = max(0.0, amount - fee)
        received = convertible_amount * mid_rate

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=amount,
            received_amount=round(received, 2),
            total_fee_czk=round(fee, 2),
            effective_rate=round(received / amount, 4) if amount > 0 else 0.0,
            markup_loss_czk=0.0,  # Wise has no hidden spread on the rate
            description="Transparent fee: 0.45% + 15 CZK, clean market rate"
        )

# 2. strategy: Revolut
class RevolutProvider(BaseProvider):
    def __init__(self):
        super().__init__("Revolut (Standard)")

    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        # In weekend days Revolut takes 1% commission for exchange
        fee_percent = 0.01 if is_weekend else 0.0
        fee = amount * fee_percent
        convertible_amount = amount - fee
        received = convertible_amount * mid_rate

        weekend_note = " (including 1% fee for weekend day)" if is_weekend else " (weekday, no fee)"

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=amount,
            received_amount=round(received, 2),
            total_fee_czk=round(fee, 2),
            effective_rate=round(received / amount, 4) if amount > 0 else 0.0,
            markup_loss_czk=0.0,
            description=f"Market rate{weekend_note}"
        )

# 3. strategy: Czech traditional bank
class CzechBankProvider(BaseProvider):
    def __init__(self):
        super().__init__("Czech Bank")
        self.markup_percent = 0.025  # 2.5% hidden markup on the rate
        self.transfer_fee_czk = 100.0 # 100 CZK for international transfer

    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        # Bank worsens the rate for the client by 2.5%
        bank_rate = mid_rate * (1 - self.markup_percent)
        convertible_amount = max(0.0, amount - self.transfer_fee_czk)
        received = convertible_amount * bank_rate

        # Calculate the hidden loss: how much would have been received at the clean rate minus what was actually received at the bank rate
        ideal_received = convertible_amount * mid_rate
        markup_loss = (ideal_received - received) / mid_rate if mid_rate > 0 else 0.0

        total_loss = self.transfer_fee_czk + markup_loss

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=amount,
            received_amount=round(received, 2),
            total_fee_czk=round(total_loss, 2),
            effective_rate=round(received / amount, 4) if amount > 0 else 0.0,
            markup_loss_czk=round(markup_loss, 2),
            description="Hidden markup on rate ~2.5% + 100 CZK transfer fee"
        )