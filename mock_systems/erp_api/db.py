from __future__ import annotations

import sqlite3
from pathlib import Path

from mock_systems.supplier_api.db import DB_PATH


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_connection()
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS erp_materials (
                material_id TEXT PRIMARY KEY,
                material_name TEXT NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS erp_products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS erp_bom (
                product_id TEXT NOT NULL,
                material_id TEXT NOT NULL,
                PRIMARY KEY (product_id, material_id)
            );
            CREATE TABLE IF NOT EXISTS erp_orders (
                order_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                supplier TEXT,
                ordered_qty INTEGER NOT NULL,
                affected_qty INTEGER NOT NULL,
                total_order_amount REAL NOT NULL,
                requester_name TEXT NOT NULL,
                requester_email TEXT NOT NULL,
                estimated_delivery_date TEXT,
                status TEXT NOT NULL
            );
            """
        )
        connection.commit()
    finally:
        connection.close()
