import sqlite3
from pathlib import Path

_DB_DIR = Path(__file__).resolve().parent
DB_PATH = str(_DB_DIR / "hospital.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
