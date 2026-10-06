from decimal import Decimal
from unittest.mock import AsyncMock, patch
import pytest

from app.services.scheduler import collect_daily_rates_job


@pytest.mark.asyncio
async def test_collect_daily_rates_job_success():
    mock_rate = Decimal("25.35")

    with patch("app.services.scheduler.rates_client.get_rate", new_callable=AsyncMock) as mock_get_rate, \
         patch("app.services.scheduler.HistoryService.upsert_rates_batch", new_callable=AsyncMock) as mock_upsert, \
         patch("app.services.scheduler.async_session_maker") as mock_session_maker:

        mock_get_rate.return_value = mock_rate
        mock_upsert.return_value = 16

        # Настраиваем контекстный менеджер async with async_session_maker()
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        await collect_daily_rates_job()

        assert mock_get_rate.call_count >= 1
        assert mock_upsert.call_count == 1

        inserted_payload = mock_upsert.call_args[0][0]
        assert len(inserted_payload) > 0
        assert inserted_payload[0]["rate"] == mock_rate

        