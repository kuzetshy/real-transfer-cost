from decimal import Decimal
from unittest.mock import AsyncMock, patch
import pytest

from app.services.scheduler import collect_daily_rates_job


@pytest.mark.asyncio
async def test_collect_daily_rates_job_success():
    # Мокаем получение курса, чтобы не идти в реальное API
    mock_rate = Decimal("25.35")

    with patch("app.services.scheduler.rates_client.get_rate", new_callable=AsyncMock) as mock_get_rate:
        mock_get_rate.return_value = mock_rate
        
        # Проверяем, что задача выполняется без исключений
        try:
            await collect_daily_rates_job()
        except Exception as exc:
            pytest.fail(f"collect_daily_rates_job raised an exception: {exc}")

        # Проверяем, что get_rate был вызван хотя бы для одной из пар
        assert mock_get_rate.call_count >= 1
        