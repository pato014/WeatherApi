from __future__ import annotations

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    city: str = Field(..., description="Normalized city name.")
    timestamp_utc: str = Field(..., description="UTC ISO timestamp for this API response.")
    source: str = Field(..., description="cache|live")
    data: dict = Field(..., description="Raw upstream payload.")


class ErrorResponse(BaseModel):
    detail: str
