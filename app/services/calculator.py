from abc import ABC, abstractmethod
from app.schemas.transfer import ProviderQuote

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        pass

class WiseProvider(BaseProvider):
    def __init__(self):
        super().__init__("Wise")
        self.percent_fee = 0.0045
        self.fixed_fee_czk = 15.0

    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        fee = (amount * self.percent_fee) + self.fixed_fee_czk
        convertible_amount = max(0.0, amount - fee)
        received = convertible_amount * mid_rate

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=amount,
            received_amount=round(received, 2),
            total_fee_czk=round(fee, 2),
            effective_rate=round(received / amount, 4) if amount > 0 else 0.0,
            markup_loss_czk=0.0,
            description="Прозрачная комиссия: 0.45% + 15 CZK, чистый биржевой курс"
        )

class RevolutProvider(BaseProvider):
    def __init__(self):
        super().__init__("Revolut (Standard)")

    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        fee_percent = 0.01 if is_weekend else 0.0
        fee = amount * fee_percent
        convertible_amount = amount - fee
        received = convertible_amount * mid_rate

        weekend_note = " (включая 1% сбор за выходной день)" if is_weekend else " (будний день, без комиссии)"

        return ProviderQuote(
            provider_name=self.name,
            sent_amount=amount,
            received_amount=round(received, 2),
            total_fee_czk=round(fee, 2),
            effective_rate=round(received / amount, 4) if amount > 0 else 0.0,
            markup_loss_czk=0.0,
            description=f"Биржевой курс{weekend_note}"
        )

class CzechBankProvider(BaseProvider):
    def __init__(self):
        super().__init__("Czech Bank")
        self.markup_percent = 0.025
        self.transfer_fee_czk = 100.0

    def calculate(self, amount: float, mid_rate: float, is_weekend: bool = False) -> ProviderQuote:
        bank_rate = mid_rate * (1 - self.markup_percent)
        convertible_amount = max(0.0, amount - self.transfer_fee_czk)
        received = convertible_amount * bank_rate

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
            description="Скрытая наценка на курс ~2.5% + 100 CZK комиссия за перевод"
        )