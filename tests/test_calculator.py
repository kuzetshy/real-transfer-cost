import pytest
from app.services.calculator import WiseProvider, RevolutProvider, CzechBankProvider

MID_RATE = 0.04  # Example: 1 CZK = 0.04 EUR (25 CZK per 1 EUR)

def test_wise_calculation():
    provider = WiseProvider()
    amount = 10000.0  # CZK
    
    # Expected fee: 10000 * 0.0045 + 15 = 45 + 15 = 60 CZK
    # Converted amount: 10000 - 60 = 9940 CZK
    # Total received in EUR: 9940 * 0.04 = 397.60 EUR
    quote = provider.calculate(amount=amount, mid_rate=MID_RATE)
    
    assert quote.provider_name == "Wise"
    assert quote.total_fee_czk == 60.0
    assert quote.received_amount == 397.6
    assert quote.markup_loss_czk == 0.0

def test_revolut_weekday_vs_weekend():
    provider = RevolutProvider()
    amount = 10000.0
    
    # Weekday: 0% fee
    weekday_quote = provider.calculate(amount=amount, mid_rate=MID_RATE, is_weekend=False)
    assert weekday_quote.total_fee_czk == 0.0
    assert weekday_quote.received_amount == 400.0  # 10000 * 0.04

    # Weekend: 1% fee applies
    weekend_quote = provider.calculate(amount=amount, mid_rate=MID_RATE, is_weekend=True)
    assert weekend_quote.total_fee_czk == 100.0  # 1% of 10000
    assert weekend_quote.received_amount == 396.0  # 9900 * 0.04

def test_czech_bank_markup_loss():
    provider = CzechBankProvider()
    amount = 10000.0
    
    # Flat 100 CZK fee leaves 9900 CZK for conversion
    # Bank exchange rate: 0.04 * (1 - 0.025) = 0.039
    # Total received: 9900 * 0.039 = 386.1 EUR
    quote = provider.calculate(amount=amount, mid_rate=MID_RATE)
    
    assert quote.provider_name == "Czech Bank"
    assert quote.received_amount == 386.1
    assert quote.markup_loss_czk > 0  # Hidden markup detected
    assert quote.received_amount < 396.0  # Bank rate is noticeably worse than Revolut or Wise