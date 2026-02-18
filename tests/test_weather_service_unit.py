import pytest
from unittest.mock import AsyncMock

from app.core.errors import CityNotFoundError, UpstreamAPIError, ValidationError
from app.services.weather_service import WeatherService


@pytest.fixture
def service():
    http = AsyncMock()
    storage = AsyncMock()
    logs = AsyncMock()
    cache = AsyncMock()

    svc = WeatherService(
        http=http,
        storage=storage,
        logs=logs,
        cache=cache,
        base_url="https://api.openweathermap.org/data/2.5/weather",
        api_key="test-key",
        units="metric",
    )
    return svc, http, storage, logs, cache


@pytest.mark.asyncio
async def test_cache_hit_returns_cached_payload(service):
    svc, http, storage, logs, cache = service

    cache.get.return_value = {"file_path": "/tmp/tbilisi.json", "fetched_at_utc": "2026-02-18T00:00:00+00:00"}
    storage.read.return_value = {"main": {"temp": 10}}

    source, data = await svc.get_weather("Tbilisi")

    assert source == "cache"
    assert data == {"main": {"temp": 10}}

    http.get_json.assert_not_called()
    storage.write.assert_not_called()
    logs.insert.assert_not_called()
    cache.set.assert_not_called()

    cache.get.assert_awaited_once_with("tbilisi")
    storage.read.assert_awaited_once_with("/tmp/tbilisi.json")


@pytest.mark.asyncio
async def test_cache_miss_fetches_upstream_stores_logs_and_sets_cache(service):
    svc, http, storage, logs, cache = service

    cache.get.return_value = None
    http.get_json.return_value = (200, {"name": "Tbilisi", "main": {"temp": 12}})
    storage.write.return_value = "/data/tbilisi_20260218T120000Z.json"

    source, data = await svc.get_weather("Tbilisi")

    assert source == "live"
    assert data["main"]["temp"] == 12

    http.get_json.assert_awaited_once()
    storage.write.assert_awaited_once()
    logs.insert.assert_awaited_once()
    cache.set.assert_awaited_once()

    # key normalization check
    cache.get.assert_awaited_once_with("tbilisi")


@pytest.mark.asyncio
async def test_upstream_404_raises_city_not_found(service):
    svc, http, storage, logs, cache = service

    cache.get.return_value = None
    http.get_json.return_value = (404, {"message": "city not found"})

    with pytest.raises(CityNotFoundError):
        await svc.get_weather("NoSuchCity")

    storage.write.assert_not_called()
    logs.insert.assert_not_called()
    cache.set.assert_not_called()


@pytest.mark.asyncio
async def test_upstream_500_raises_upstream_error(service):
    svc, http, storage, logs, cache = service

    cache.get.return_value = None
    http.get_json.return_value = (500, {"message": "error"})

    with pytest.raises(UpstreamAPIError) as e:
        await svc.get_weather("Tbilisi")

    assert e.value.status_code == 500
    storage.write.assert_not_called()
    logs.insert.assert_not_called()
    cache.set.assert_not_called()


@pytest.mark.asyncio
async def test_empty_city_raises_validation_error(service):
    svc, http, storage, logs, cache = service

    with pytest.raises(ValidationError):
        await svc.get_weather("   ")

    http.get_json.assert_not_called()
    storage.write.assert_not_called()
    logs.insert.assert_not_called()
    cache.set.assert_not_called()
