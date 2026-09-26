# app/services/calculator.py
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Union
from app.schemas.transfer import ProviderQuote

Numeric = Union[float, Decimal]


class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(self, amount: Numeric, mid_rate: Numeric, is_weekend: bool = False) -> ProviderQuote:
        pass


class WiseProvider(BaseProvider):
    def __init__(self):
        super().__init__("Wise")
        self.percent_fee = Decimal("0.0045")
        self.fixed_fee_czk = Decimal("15.0")

    def calculate(self, amount: Numeric, mid_rate: Numeric, is_weekend: bool = False) -> ProviderQuote:
        amt = Decimal(str(amount))
        rate = Decimal(str(mid_rate))

        fee = (amt * self.percent_fee) + self.fixed_fee_czk
        convertible_amount = max(Decimal("0.0"), amt - fee)
        received = convertible_amount * rate

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=float(amt),
            received_amount=round(float(received), 2),
            total_fee_czk=round(float(fee), 2),
            effective_rate=round(float(received / amt), 4) if amt > 0 else 0.0,
            markup_loss_czk=0.0,
            description="Прозрачная комиссия: 0.45% + 15 CZK, чистый биржевой курс"
        )


class RevolutProvider(BaseProvider):
    def __init__(self):
        super().__init__("Revolut (Standard)")

    def calculate(self, amount: Numeric, mid_rate: Numeric, is_weekend: bool = False) -> ProviderQuote:
        amt = Decimal(str(amount))
        rate = Decimal(str(mid_rate))

        fee_percent = Decimal("0.01") if is_weekend else Decimal("0.0")
        fee = amt * fee_percent
        convertible_amount = amt - fee
        received = convertible_amount * rate

        weekend_note = " (включая 1% сбор за выходной день)" if is_weekend else " (будний день, без комиссии)"

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=float(amt),
            received_amount=round(float(received), 2),
            total_fee_czk=round(float(fee), 2),
            effective_rate=round(float(received / amt), 4) if amt > 0 else 0.0,
            markup_loss_czk=0.0,
            description=f"Биржевой курс{weekend_note}"
        )


class CzechBankProvider(BaseProvider):
    def __init__(self):
        super().__init__("Czech Bank")
        self.markup_percent = Decimal("0.025")
        self.transfer_fee_czk = Decimal("100.0")

    def calculate(self, amount: Numeric, mid_rate: Numeric, is_weekend: bool = False) -> ProviderQuote:
        amt = Decimal(str(amount))
        rate = Decimal(str(mid_rate))

        bank_rate = rate * (Decimal("1.0") - self.markup_percent)
        convertible_amount = max(Decimal("0.0"), amt - self.transfer_fee_czk)
        received = convertible_amount * bank_rate

        ideal_received = convertible_amount * rate
        markup_loss = (ideal_received - received) / rate if rate > 0 else Decimal("0.0")
        total_loss = self.transfer_fee_czk + markup_loss

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=float(amt),
            received_amount=round(float(received), 2),
            total_fee_czk=round(float(total_loss), 2),
            effective_rate=round(float(received / amt), 4) if amt > 0 else 0.0,
            markup_loss_czk=round(float(markup_loss), 2),
            description="Скрытая наценка на курс ~2.5% + 100 CZK комиссия за перевод"
        )
    