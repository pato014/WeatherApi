from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherError(Exception):
    message: str


@dataclass(frozen=True)
class CityNotFoundError(WeatherError):
    pass


@dataclass(frozen=True)
class UpstreamAPIError(WeatherError):
    status_code: int | None = None


@dataclass(frozen=True)
class ValidationError(WeatherError):
    pass
