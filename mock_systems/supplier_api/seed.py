from __future__ import annotations

from mock_systems.supplier_api.db import get_connection, init_db

# 3 "new" events span the demo cases: two high-confidence (validate), one noisy (discard).
_SEED_EVENTS = [
    ("EVT-9001", "DYE-NAVY-4052", "shipment_delay", "high", 7, "2026-08-21T06:14:00Z", "new"),
    ("EVT-9002", "FAB-COTTON-118", "shortage", "medium", 4, "2026-08-20T09:00:00Z", "new"),
    ("EVT-9003", "THR-POLY-22", "quality_hold", "low", 2, "2026-08-15T11:30:00Z", "processed"),
    ("EVT-9004", "DYE-NAVY-4052", "shipment_delay", "high", 5, "2026-08-10T08:00:00Z", "processed"),
    ("EVT-9005", "ZIP-METAL-09", "shortage", "low", 1, "2026-08-09T10:00:00Z", "processed"),
    ("EVT-9006", "FAB-COTTON-118", "quality_hold", "medium", 3, "2026-08-05T13:00:00Z", "processed"),
    ("EVT-9007", "DYE-NAVY-4052", "shipment_delay", "low", 1, "2026-08-22T07:00:00Z", "new"),
    ("EVT-9008", "THR-POLY-22", "shortage", "high", 6, "2026-08-01T09:00:00Z", "processed"),
]


def seed_events() -> None:
    init_db()
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT OR IGNORE INTO disruption_events
                (event_id, material_id, event_type, severity, estimated_duration_days, reported_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            _SEED_EVENTS,
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    seed_events()
