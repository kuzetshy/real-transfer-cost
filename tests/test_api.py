# tests/test_api.py
import pytest
import httpx
import respx
from app.main import app

@pytest.mark.asyncio
@respx.mock
async def test_compare_quotes_success():
    # 1. Мокаем внешний API Frankfurter
    respx.get("https://api.frankfurter.dev/v1/latest?from=EUR&to=CZK").mock(
        return_value=httpx.Response(200, json={"rates": {"CZK": "25.30"}})
    )

    # 2. Вызываем наш реальный GET-эндпоинт через ASGITransport
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/compare",
            params={"from_currency": "EUR", "to_currency": "CZK", "amount": 1000.0}
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    # Проверяем, что первый результат отсортирован по максимуму received_amount 🏆
    assert data[0]["received_amount"] >= data[1]["received_amount"]