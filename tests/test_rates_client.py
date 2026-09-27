import pytest
import respx
import httpx
from datetime import date
from decimal import Decimal
from app.services.rates import RatesClient

@pytest.mark.asyncio
@respx.mock
async def test_get_historical_rates_success():
    client = RatesClient()
    start_date = date(2026, 9, 1)
    end_date = date(2026, 9, 2)

    # Мокаем ответ от Frankfurter API
    mock_url = f"{client.BASE_URL}/2026-09-01..2026-09-02"
    mock_response = {
        "amount": 1.0,
        "base": "EUR",
        "start_date": "2026-09-01",
        "end_date": "2026-09-02",
        "rates": {
            "2026-09-01": {"CZK": 25.105},
            "2026-09-02": {"CZK": 25.200},
        },
    }

    respx.get(mock_url).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    result = await client.get_historical_rates(
        base="EUR",
        symbols=["CZK"],
        start_date=start_date,
        end_date=end_date,
    )

    # Проверяем структуру и типы
    assert len(result) == 2
    assert date(2026, 9, 1) in result
    assert result[date(2026, 9, 1)]["CZK"] == Decimal("25.105")
    assert result[date(2026, 9, 2)]["CZK"] == Decimal("25.200")