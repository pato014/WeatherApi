from __future__ import annotations

import json
from typing import Any, Optional

from redis.asyncio import Redis


class RedisCache:
    """
    Cache stores only small metadata:
      key: weather:{city_lower}
      value: {"file_path": "...", "fetched_at_utc": "..."}  (JSON string)
      TTL: 300s
    """

    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl = ttl_seconds

    @staticmethod
    def _key(city_lower: str) -> str:
        return f"weather:{city_lower}"

    async def get(self, city_lower: str) -> Optional[dict[str, Any]]:
        raw = await self._redis.get(self._key(city_lower))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    async def set(self, city_lower: str, value: dict[str, Any]) -> None:
        raw = json.dumps(value, ensure_ascii=False)
        await self._redis.set(self._key(city_lower), raw, ex=self._ttl)
