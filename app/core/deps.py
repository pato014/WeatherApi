from __future__ import annotations

from typing import Optional

from app.services.weather_service import WeatherService

_service: Optional[WeatherService] = None


def set_weather_service(service: WeatherService) -> None:
    global _service
    _service = service


def get_weather_service() -> WeatherService:
    if _service is None:
        raise RuntimeError("WeatherService is not initialized yet.")
    return _service
