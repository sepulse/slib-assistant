from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from slib_assistant.models import BookMetadata, ProviderRecord


class MetadataCache:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS books (
                    isbn13 TEXT PRIMARY KEY,
                    resolved_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_results (
                    isbn13 TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    PRIMARY KEY (isbn13, provider)
                );
                CREATE TABLE IF NOT EXISTS lookup_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn13 TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def get(self, isbn13: str, ttl_days: int) -> BookMetadata | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT resolved_json, updated_at FROM books WHERE isbn13 = ?",
                (isbn13,),
            ).fetchone()
        if row is None:
            return None
        updated = datetime.fromisoformat(row["updated_at"])
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - updated > timedelta(days=ttl_days):
            return None
        return BookMetadata.from_dict(json.loads(row["resolved_json"]))

    def put(self, metadata: BookMetadata, records: list[ProviderRecord]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO books(isbn13, resolved_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(isbn13) DO UPDATE SET
                    resolved_json=excluded.resolved_json,
                    updated_at=excluded.updated_at
                """,
                (
                    metadata.isbn13,
                    json.dumps(metadata.to_dict(), ensure_ascii=False),
                    now,
                ),
            )
            for record in records:
                payload = {
                    "provider": record.provider,
                    "isbn13": record.isbn13,
                    "data": record.data,
                    "raw": record.raw,
                    "fetched_at": record.fetched_at,
                }
                db.execute(
                    """
                    INSERT INTO provider_results(isbn13, provider, result_json, fetched_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(isbn13, provider) DO UPDATE SET
                        result_json=excluded.result_json,
                        fetched_at=excluded.fetched_at
                    """,
                    (
                        metadata.isbn13,
                        record.provider,
                        json.dumps(payload, ensure_ascii=False),
                        record.fetched_at or now,
                    ),
                )

    def log_lookup(self, isbn13: str, status: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO lookup_log(isbn13, status, created_at) VALUES (?, ?, ?)",
                (isbn13, status, datetime.now(timezone.utc).isoformat()),
            )
