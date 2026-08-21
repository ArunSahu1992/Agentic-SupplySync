from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "supplysync.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
