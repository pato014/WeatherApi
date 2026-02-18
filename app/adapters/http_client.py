from __future__ import annotations
import httpx


class WeatherHttpClient:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout = httpx.Timeout(timeout_seconds)

    async def get_json(self, url: str, params: dict) -> tuple[int, dict]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url, params=params)
            return resp.status_code, resp.json()
