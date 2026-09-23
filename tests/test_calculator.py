import pytest
from app.services.calculator import WiseProvider, RevolutProvider, CzechBankProvider

MID_RATE = 0.04  # Допустим, 1 CZK = 0.04 EUR (25 CZK за 1 EUR)

def test_wise_calculation():
    provider = WiseProvider()
    amount = 10000.0  # CZK
    
    # Ожидаемая комиссия: 10000 * 0.0045 + 15 = 45 + 15 = 60 CZK
    # Сумма к конвертации: 10000 - 60 = 9940 CZK
    # Итого в EUR: 9940 * 0.04 = 397.60 EUR
    quote = provider.calculate(amount=amount, mid_rate=MID_RATE)
    
    assert quote.provider_name == "Wise"
    assert quote.total_fee_czk == 60.0
    assert quote.received_amount == 397.6
    assert quote.markup_loss_czk == 0.0

def test_revolut_weekday_vs_weekend():
    provider = RevolutProvider()
    amount = 10000.0
    
    # Будний день: 0% комиссии
    weekday_quote = provider.calculate(amount=amount, mid_rate=MID_RATE, is_weekend=False)
    assert weekday_quote.total_fee_czk == 0.0
    assert weekday_quote.received_amount == 400.0  # 10000 * 0.04

    # Выходной день: 1% комиссии
    weekend_quote = provider.calculate(amount=amount, mid_rate=MID_RATE, is_weekend=True)
    assert weekend_quote.total_fee_czk == 100.0  # 1% от 10000
    assert weekend_quote.received_amount == 396.0  # 9900 * 0.04

def test_czech_bank_markup_loss():
    provider = CzechBankProvider()
    amount = 10000.0
    
    # Фикс 100 CZK комиссии, остается 9900 CZK
    # Банковский курс: 0.04 * (1 - 0.025) = 0.039
    # Получено: 9900 * 0.039 = 386.1 EUR
    quote = provider.calculate(amount=amount, mid_rate=MID_RATE)
    
    assert quote.provider_name == "Czech Bank"
    assert quote.received_amount == 386.1
    assert quote.markup_loss_czk > 0  # Скрытая потеря зафиксирована
    assert quote.received_amount < 396.0  # Банк явно хуже Revolut и Wise
    