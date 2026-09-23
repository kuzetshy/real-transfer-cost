import httpx
from fastapi import HTTPException

class RatesClient:
    BASE_URL = "https://api.frankfurter.dev/v1"

    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()

        if from_curr == to_curr:
            return 1.0

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

                return float(data["rates"][to_curr])
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