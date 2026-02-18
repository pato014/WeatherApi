from __future__ import annotations

from datetime import datetime, timezone

from app.adapters.http_client import WeatherHttpClient
from app.adapters.redis_cache import RedisCache
from app.adapters.sqlite_repo import SQLiteLogRepo, LogEntry
from app.adapters.storage import LocalJsonStorage
from app.core.errors import CityNotFoundError, UpstreamAPIError, ValidationError


class WeatherService:
    def __init__(
        self,
        http: WeatherHttpClient,
        storage: LocalJsonStorage,
        logs: SQLiteLogRepo,
        cache: RedisCache,
        base_url: str,
        api_key: str,
        units: str,
    ) -> None:
        self._http = http
        self._storage = storage
        self._logs = logs
        self._cache = cache
        self._base_url = base_url
        self._api_key = api_key
        self._units = units

    @staticmethod
    def _normalize_city(city: str) -> str:
        city_norm = " ".join(city.strip().split())
        if not city_norm:
            raise ValidationError("City must be a non-empty string.")
        if len(city_norm) > 120:
            raise ValidationError("City is too long.")
        return city_norm

    async def get_weather(self, city: str) -> tuple[str, dict]:
        city_norm = self._normalize_city(city)
        city_lower = city_norm.lower()

        cached = await self._cache.get(city_lower)
        if cached and "file_path" in cached:
            data = await self._storage.read(cached["file_path"])
            return "cache", data

        params = {"q": city_norm, "appid": self._api_key, "units": self._units}
        status, data = await self._http.get_json(self._base_url, params=params)

        if status == 404:
            raise CityNotFoundError(f"City not found: {city_norm}")
        if status >= 400:
            raise UpstreamAPIError("Upstream weather API error.", status_code=status)

        now = datetime.now(timezone.utc)
        file_path = await self._storage.write(city_norm, data, ts=now)

        await self._logs.insert(LogEntry(city=city_norm, timestamp_utc=now, file_path=file_path))
        await self._cache.set(city_lower, {"file_path": file_path, "fetched_at_utc": now.isoformat()})

        return "live", data
