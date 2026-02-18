from __future__ import annotations

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.routes import router
from app.adapters.http_client import WeatherHttpClient
from app.adapters.redis_cache import RedisCache
from app.adapters.sqlite_repo import SQLiteLogRepo
from app.adapters.storage import LocalJsonStorage
from app.core.config import settings
from app.core.deps import set_weather_service
from app.core.logging import configure_logging
from app.services.weather_service import WeatherService


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title=settings.app_name)
    app.include_router(router)

    @app.on_event("startup")
    async def startup() -> None:
        redis = Redis.from_url(settings.redis_url, decode_responses=False)
        cache = RedisCache(redis=redis, ttl_seconds=settings.cache_ttl_seconds)

        logs = SQLiteLogRepo(db_path=settings.sqlite_path)
        await logs.init()

        http = WeatherHttpClient(timeout_seconds=settings.http_timeout_seconds)
        storage = LocalJsonStorage(data_dir=settings.data_dir)

        service = WeatherService(
            http=http,
            storage=storage,
            logs=logs,
            cache=cache,
            base_url=settings.openweather_base_url,
            api_key=settings.openweather_api_key,
            units=settings.units,
        )
        set_weather_service(service)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        # Optional: close redis cleanly if you keep a reference
        pass

    return app


app = create_app()
