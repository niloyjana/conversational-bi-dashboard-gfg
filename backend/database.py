import sqlite3
import pandas as pd
import os
import time
import re
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "claims.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "insurance_claims.csv")
TABLE_NAME = "claims"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def load_csv_to_db(csv_path: str = CSV_PATH, table: str = TABLE_NAME) -> dict:
    """Load (or replace) a CSV into SQLite and return schema info."""
    df = pd.read_csv(csv_path)

    # Normalize column names: lowercase, replace spaces/special chars with _
    df.columns = [
        re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")
        for c in df.columns
    ]

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.close()

    return {
        "table": table,
        "columns": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "row_count": len(df),
    }


def get_table_info(table: str = TABLE_NAME) -> dict:
    """Return column names, types, and a few sample rows."""
    conn = get_connection()
    try:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        cols = [{"name": r["name"], "type": r["type"]} for r in cursor.fetchall()]
        if not cols:
            return {"error": f"Table '{table}' not found. Upload a dataset first."}

        sample = conn.execute(f"SELECT * FROM {table} LIMIT 3").fetchall()
        sample_rows = [dict(r) for r in sample]

        row_count_row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
        row_count = row_count_row["cnt"] if row_count_row else 0

        return {
            "table": table,
            "columns": [c["name"] for c in cols],
            "column_details": cols,
            "sample_rows": sample_rows,
            "row_count": row_count,
        }
    finally:
        conn.close()


def execute_query(sql: str) -> dict:
    """Execute a SELECT query and return results + timing."""
    start = time.perf_counter()
    conn = get_connection()
    try:
        # Safety: only allow SELECT
        clean = sql.strip().lstrip(";").strip()
        if not clean.upper().startswith("SELECT"):
            return {"error": "Only SELECT queries are allowed.", "data": [], "row_count": 0}

        cursor = conn.execute(clean)
        rows = [dict(r) for r in cursor.fetchall()]
        elapsed = round(time.perf_counter() - start, 3)
        return {
            "data": rows,
            "row_count": len(rows),
            "execution_time": elapsed,
            "columns": [d[0] for d in cursor.description] if cursor.description else [],
        }
    except Exception as e:
        return {"error": str(e), "data": [], "row_count": 0, "execution_time": 0}
    finally:
        conn.close()


# Auto-load default CSV on import if DB doesn't exist
if not os.path.exists(DB_PATH) and os.path.exists(CSV_PATH):
    load_csv_to_db()
