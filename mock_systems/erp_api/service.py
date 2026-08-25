from __future__ import annotations

from typing import Any

from mock_systems.erp_api.db import get_connection, init_db


def get_material(material_id: str) -> dict[str, Any] | None:
    init_db()
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM erp_materials WHERE material_id = ?", (material_id,)
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row else None


def get_affected_orders(material_id: str) -> list[dict[str, Any]]:
    init_db()
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT o.*, p.product_name
            FROM erp_orders o
            JOIN erp_bom b ON b.product_id = o.product_id
            JOIN erp_products p ON p.product_id = o.product_id
            WHERE b.material_id = ? AND o.status IN ('open', 'confirmed')
            ORDER BY o.estimated_delivery_date ASC, o.order_id ASC
            """,
            (material_id,),
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]
