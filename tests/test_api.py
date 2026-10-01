# tests/test_api.py
import pytest
import httpx
import respx
from app.db.session import get_db
from app.main import app
from datetime import date
from decimal import Decimal
from app.db.models import ExchangeRateHistory
from app.services.history import HistoryService
from tests.conftest import db_session
from httpx import AsyncClient, ASGITransport


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

@pytest.mark.asyncio
async def test_get_rates_history_endpoint(client, db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Берем дату, которой гарантированно нет в базе от сидинга
    test_date = date(2000, 1, 15)

    service = HistoryService(db_session)
    await service.upsert_rates_batch([
        {
            "base_currency": "EUR",
            "target_currency": "CZK",
            "rate": Decimal("25.123400"),
            "rate_date": test_date,
            "provider": "frankfurter",
        }
    ])

    try:
        response = await client.get(
            f"/api/v1/rates/history?base=EUR&target=CZK&from_date={test_date.isoformat()}&to_date={test_date.isoformat()}"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["base_currency"] == "EUR"
        assert data["target_currency"] == "CZK"
        assert data["points_count"] >= 1
        assert any(p["date"] == test_date.isoformat() for p in data["history"])
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cors_headers_allowed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        }
        response = await ac.options("/api/v1/rates", headers=headers)
        
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "GET" in response.headers.get("access-control-allow-methods", "")