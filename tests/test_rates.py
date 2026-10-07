import pytest
import httpx
import respx
from decimal import Decimal
from app.services.rates import RatesClient

@pytest.mark.asyncio
@respx.mock
async def test_rates_client_success_and_cache():
    client = RatesClient()
    
    # Mock external Frankfurter API response 🎭
    respx.get("https://api.frankfurter.dev/v1/latest?from=EUR&to=CZK").mock(
        return_value=httpx.Response(200, json={"rates": {"CZK": 25.40}})
    )

    # 1. Initial call — makes external network request 🌐
    rate_first = await client.get_rate("eur", "czk")
    assert rate_first == Decimal("25.40")

    # 2. Subsequent call — resolves immediately from cache ⚡
    # Clear mocks to verify no further network requests are dispatched
    respx.clear()
    
    rate_cached = await client.get_rate("EUR", "CZK")
    assert rate_cached == Decimal("25.40")


@pytest.mark.asyncio
async def test_same_currency_returns_one():
    client = RatesClient()
    rate = await client.get_rate("USD", "usd")
    assert rate == Decimal("1.0")