from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

from sieu_thi_mini_app.utils.constants import DEFAULT_DB_PATH

SqlParams = Sequence[Any] | Mapping[str, Any] | None


class Database:
    """Small SQLite gateway with explicit transactions and row dictionaries."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._connection: sqlite3.Connection | None = None

    @classmethod
    def from_default_path(cls) -> "Database":
        configured_path = os.getenv("SIEU_THI_MINI_DB")
        return cls(configured_path or DEFAULT_DB_PATH)

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.db_path, isolation_level=None)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = WAL")
        return self._connection

    def initialize(self) -> None:
        schema_sql = _read_sql_file("create_tables.sql")
        seed_sql = _read_sql_file("seed_data.sql")
        self.connection.executescript(schema_sql)
        self.connection.executescript(seed_sql)

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        conn = self.connection
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def execute(self, sql: str, params: SqlParams = None) -> sqlite3.Cursor:
        return self.connection.execute(sql, params or ())

    def execute_many(self, sql: str, rows: Iterable[SqlParams]) -> sqlite3.Cursor:
        return self.connection.executemany(sql, rows)

    def fetch_one(self, sql: str, params: SqlParams = None) -> dict[str, Any] | None:
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, sql: str, params: SqlParams = None) -> list[dict[str, Any]]:
        cursor = self.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def _read_sql_file(filename: str) -> str:
    path = Path(__file__).with_name(filename)
    return path.read_text(encoding="utf-8")
