from __future__ import annotations

from mock_systems.erp_api.db import get_connection, init_db

_MATERIALS = [
    ("DYE-NAVY-4052", "Navy dye", "delayed"),
    ("FAB-COTTON-118", "Cotton fabric", "available"),
    ("THR-POLY-22", "Polyester thread", "available"),
]
_PRODUCTS = [
    ("PROD-NAVY-DRESS", "Navy dress"),
    ("PROD-COTTON-SHIRT", "Cotton shirt"),
]
_BOM = [
    ("PROD-NAVY-DRESS", "DYE-NAVY-4052"),
    ("PROD-COTTON-SHIRT", "FAB-COTTON-118"),
]
_ORDERS = [
    ("ORD-4521", "PROD-NAVY-DRESS", "Northwind Components", 200, 200, 24000.0, "Asha Rao", "asha@example.com", "2026-09-02", "open"),
    ("ORD-4522", "PROD-NAVY-DRESS", "Summit Plastics", 80, 80, 9600.0, "Ben Carter", "ben@example.com", "2026-09-05", "confirmed"),
    ("ORD-4523", "PROD-COTTON-SHIRT", "Blue Harbor Logistics", 100, 0, 7000.0, "Cara Singh", "cara@example.com", "2026-09-03", "open"),
]


def seed_data() -> None:
    init_db()
    connection = get_connection()
    try:
        connection.executemany("INSERT OR IGNORE INTO erp_materials VALUES (?, ?, ?)", _MATERIALS)
        connection.executemany("INSERT OR IGNORE INTO erp_products VALUES (?, ?)", _PRODUCTS)
        connection.executemany("INSERT OR IGNORE INTO erp_bom VALUES (?, ?)", _BOM)
        connection.executemany("INSERT OR IGNORE INTO erp_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", _ORDERS)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    seed_data()
