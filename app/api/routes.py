from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.core.deps import get_weather_service
from app.core.errors import CityNotFoundError, UpstreamAPIError, ValidationError
from app.models.schemas import WeatherResponse, ErrorResponse
router = APIRouter(tags=["weather"])


@router.get(
    "/weather",
    response_model=WeatherResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
    summary="Get current weather for a city",
    description="Async fetch from OpenWeatherMap, cache via Redis (5 min), store JSON to /data, log to SQLite.",
)
async def weather(
    city: str = Query(..., min_length=1, description="City name, e.g., 'Tbilisi'"),
    svc=Depends(get_weather_service),
):
    try:
        source, data = await svc.get_weather(city)
        city_norm = " ".join(city.strip().split())
        return WeatherResponse(
            city=city_norm,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            source=source,
            data=data,
        )
    except ValidationError as e:
        return JSONResponse(status_code=400, content={"detail": e.message})
    except CityNotFoundError as e:
        return JSONResponse(status_code=404, content={"detail": e.message})
    except UpstreamAPIError as e:
        return JSONResponse(status_code=502, content={"detail": e.message})
