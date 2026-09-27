from datetime import date
from decimal import Decimal
from typing import Dict
from cachetools import TTLCache
from fastapi import HTTPException
import httpx


class RatesClient:
    BASE_URL = "https://api.frankfurter.dev/v1"

    def __init__(self, cache_maxsize: int = 100, cache_ttl: int = 600):
        self._cache: TTLCache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    async def get_rate(self, from_currency: str, to_currency: str) -> Decimal:
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()

        if from_curr == to_curr:
            return Decimal("1.0")

        cache_key = f"{from_curr}_{to_curr}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/latest",
                    params={"from": from_curr, "to": to_curr}
                )
                response.raise_for_status()
                data = response.json()

                if "rates" not in data or to_curr not in data["rates"]:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Currency pair {from_curr}->{to_curr} not supported."
                    )

                rate = Decimal(str(data["rates"][to_curr]))
                self._cache[cache_key] = rate
                return rate

            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"External API error: {exc.response.text}"
                )

            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=503,
                    detail=f"Network error while fetching rates: {str(exc)}"
                )

    async def get_historical_rates(
        self,
        base: str,
        symbols: list[str],
        start_date: date,
        end_date: date,
    ) -> dict[date, dict[str, Decimal]]:
        # Используем self.BASE_URL
        url = f"{self.BASE_URL}/{start_date.isoformat()}..{end_date.isoformat()}"
        params = {
            "from": base.upper(),
            "to": ",".join(s.upper() for s in symbols),
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        raw_rates = data.get("rates", {})
        parsed_rates: dict[date, dict[str, Decimal]] = {}

        for d_str, symbol_map in raw_rates.items():
            parsed_date = date.fromisoformat(d_str)
            parsed_rates[parsed_date] = {
                curr: Decimal(str(val)) for curr, val in symbol_map.items()
            }

        return parsed_rates


rates_client = RatesClient()