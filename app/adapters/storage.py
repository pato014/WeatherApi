from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import anyio


def safe_city(city: str) -> str:
    cleaned = "".join(ch for ch in city.strip().lower().replace(" ", "_") if ch.isalnum() or ch in {"_", "-"})
    return cleaned or "unknown"


class LocalJsonStorage:
    def __init__(self, data_dir: str) -> None:
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    async def write(self, city: str, payload: dict[str, Any], ts: datetime) -> str:
        filename = f"{safe_city(city)}_{ts.strftime('%Y%m%dT%H%M%SZ')}.json"
        path = self._dir / filename
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

        def _sync_write() -> None:
            path.write_bytes(raw)

        await anyio.to_thread.run_sync(_sync_write)
        return str(path)

    async def read(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)

        def _sync_read() -> dict[str, Any]:
            return json.loads(path.read_bytes().decode("utf-8"))

        return await anyio.to_thread.run_sync(_sync_read)
