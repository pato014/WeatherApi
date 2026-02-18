from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime

import anyio


@dataclass(frozen=True)
class LogEntry:
    city: str
    timestamp_utc: datetime
    file_path: str


class SQLiteLogRepo:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def init(self) -> None:
        def _sync_init() -> None:
            con = sqlite3.connect(self._db_path)
            try:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS logs ( 
                        id INTEGER PRIMARY KEY AUTOINCREMENT,  
                        city TEXT NOT NULL, 
                        timestamp_utc TEXT NOT NULL,
                        file_path TEXT NOT NULL
                    )
                    """
                )
                con.commit()
            finally:
                con.close()

        await anyio.to_thread.run_sync(_sync_init)

    async def insert(self, entry: LogEntry) -> None:
        def _sync_insert() -> None:
            con = sqlite3.connect(self._db_path)
            try:
                con.execute(
                    "INSERT INTO logs (city, timestamp_utc, file_path) VALUES (?, ?, ?)",
                    (entry.city, entry.timestamp_utc.isoformat(), entry.file_path),
                )
                con.commit()
            finally:
                con.close()

        await anyio.to_thread.run_sync(_sync_insert)
