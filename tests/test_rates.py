import pytest
import httpx
import respx
from decimal import Decimal
from app.services.rates import RatesClient

@pytest.mark.asyncio
@respx.mock
async def test_rates_client_success_and_cache():
    client = RatesClient()
    
    # Мокаем внешний API Frankfurter 🎭
    respx.get("https://api.frankfurter.dev/v1/latest?from=EUR&to=CZK").mock(
        return_value=httpx.Response(200, json={"rates": {"CZK": 25.40}})
    )

    # 1. Первый вызов — должен пойти в сеть 🌐
    rate_first = await client.get_rate("eur", "czk")
    assert rate_first == Decimal("25.40")

    # 2. Второй вызов — должен взяться из кэша мгновенно (сеть отключена, мок не сработает повторно) ⚡
    # Убираем мок, чтобы убедиться, что запрос в сеть НЕ идет
    respx.clear()
    
    rate_cached = await client.get_rate("EUR", "CZK")
    assert rate_cached == Decimal("25.40")


@pytest.mark.asyncio
async def test_same_currency_returns_one():
    client = RatesClient()
    rate = await client.get_rate("USD", "usd")
    assert rate == Decimal("1.0")