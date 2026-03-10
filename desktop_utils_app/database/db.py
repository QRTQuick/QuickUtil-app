from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from core.app_dirs import db_path


SCHEMA_VERSION = 1


def _apply_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          start_ts INTEGER NOT NULL,
          end_ts INTEGER,
          notes TEXT
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_events_start ON events(start_ts);")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alarms (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          label TEXT NOT NULL,
          ts INTEGER NOT NULL,
          enabled INTEGER NOT NULL DEFAULT 1,
          kind TEXT NOT NULL DEFAULT 'alarm',
          fired INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alarms_ts ON alarms(ts);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alarms_enabled ON alarms(enabled, fired);")

    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', ?);",
        (str(SCHEMA_VERSION),),
    )
    conn.commit()


class Database:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or db_path("QuickUtil")
        self._init_lock = threading.Lock()
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            with self.connect() as conn:
                _apply_schema(conn)
            self._initialized = True

    @contextmanager
    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, timeout=8)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def session(self) -> sqlite3.Connection:
        self._ensure_initialized()
        with self.connect() as conn:
            yield conn

