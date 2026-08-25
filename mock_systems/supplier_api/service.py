from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from mock_systems.supplier_api.db import get_connection, init_db


def list_events(since: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    init_db()
    query = "SELECT * FROM disruption_events WHERE 1=1"
    params: list[str] = []
    if since:
        query += " AND reported_at >= ?"
        params.append(since)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY reported_at ASC"
    connection = get_connection()
    try:
        rows = connection.execute(query, params).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


def get_event(event_id: str) -> dict[str, Any] | None:
    init_db()
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM disruption_events WHERE event_id = ?", (event_id,)
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row is not None else None


def ack_event(event_id: str) -> dict[str, str]:
    init_db()
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT event_id FROM disruption_events WHERE event_id = ?", (event_id,)
        ).fetchone()
        if row is None:
            raise KeyError(event_id)
        connection.execute(
            "UPDATE disruption_events SET status = 'processed' WHERE event_id = ?",
            (event_id,),
        )
        connection.commit()
    finally:
        connection.close()
    return {"event_id": event_id, "status": "processed"}


def insert_event(
    event_id: str,
    material_id: str,
    event_type: str,
    severity: str,
    estimated_duration_days: int | None = None,
    reported_at: str | None = None,
) -> dict[str, Any]:
    init_db()
    reported_at = reported_at or datetime.now(timezone.utc).isoformat()
    connection = get_connection()
    try:
        try:
            connection.execute(
                """
                INSERT INTO disruption_events
                    (event_id, material_id, event_type, severity, estimated_duration_days, reported_at, status)
                VALUES (?, ?, ?, ?, ?, ?, 'new')
                """,
                (event_id, material_id, event_type, severity, estimated_duration_days, reported_at),
            )
            connection.commit()
            return {"event_id": event_id, "status": "new", "created": True}
        except sqlite3.IntegrityError:
            row = connection.execute(
                "SELECT status FROM disruption_events WHERE event_id = ?", (event_id,)
            ).fetchone()
            return {"event_id": event_id, "status": row["status"], "created": False}
    finally:
        connection.close()


def reset_events() -> None:
    init_db()
    connection = get_connection()
    try:
        connection.execute("DELETE FROM disruption_events")
        connection.commit()
    finally:
        connection.close()
