from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "supplysync.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS disruption_events (
                event_id TEXT PRIMARY KEY,
                material_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                estimated_duration_days INTEGER,
                reported_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new'
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
