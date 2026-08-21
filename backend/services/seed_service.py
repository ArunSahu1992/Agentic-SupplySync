from __future__ import annotations

from backend.database.db import get_connection


def seed_initial_data() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
            """
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO suppliers (id, name, status)
            VALUES (1, 'Northwind Components', 'active'),
                   (2, 'Summit Plastics', 'monitoring'),
                   (3, 'Blue Harbor Logistics', 'active')
            """
        )

        connection.commit()
