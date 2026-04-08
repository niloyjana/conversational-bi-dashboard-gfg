"""
Decide which Plotly chart type to use based on query result structure.
"""
from typing import Any


def select_chart(data: list[dict], sql: str, question: str) -> dict:
    if not data:
        return {"type": "table", "title": "Query Results"}

    cols = list(data[0].keys())
    num_cols = [c for c in cols if _is_numeric(data, c)]
    cat_cols = [c for c in cols if c not in num_cols]
    sql_upper = sql.upper()
    q_lower = question.lower()

    # ── Time-series → line chart ──────────────────────────────────────────
    time_keywords = ["year", "month", "date", "quarter", "trend", "over time", "by year", "by month"]
    has_time_col = any(k in " ".join(cols).lower() for k in ["year", "month", "date", "quarter"])
    asks_trend = any(k in q_lower for k in ["trend", "over time", "by year", "by month", "monthly", "yearly"])

    if (has_time_col or asks_trend) and num_cols and len(data) > 1:
        x_col = next((c for c in cols if any(k in c.lower() for k in ["year", "month", "date", "quarter"])), cols[0])
        y_cols = num_cols[:3]
        return {
            "type": "line",
            "x": x_col,
            "y": y_cols if len(y_cols) > 1 else y_cols[0],
            "title": _make_title(question),
        }

    # ── Proportion / share → pie chart ───────────────────────────────────
    pie_words = ["proportion", "share", "breakdown", "distribution", "percentage", "ratio", "pie"]
    if any(w in q_lower for w in pie_words) and cat_cols and num_cols and len(data) <= 15:
        return {
            "type": "pie",
            "names": cat_cols[0],
            "values": num_cols[0],
            "title": _make_title(question),
        }

    # ── Correlation / two numerics → scatter ─────────────────────────────
    if len(num_cols) >= 2 and len(cat_cols) == 0 and "correlat" in q_lower:
        return {
            "type": "scatter",
            "x": num_cols[0],
            "y": num_cols[1],
            "title": _make_title(question),
        }

    # ── Single category + single metric → bar chart ───────────────────────
    if cat_cols and num_cols:
        color_col = cat_cols[1] if len(cat_cols) > 1 else None
        return {
            "type": "bar",
            "x": cat_cols[0],
            "y": num_cols[0],
            "color": color_col,
            "title": _make_title(question),
        }

    # ── Wide tables → table view ──────────────────────────────────────────
    return {"type": "table", "title": _make_title(question)}


def _is_numeric(data: list[dict], col: str) -> bool:
    """Check if a column is predominantly numeric."""
    vals = [r[col] for r in data[:20] if r[col] is not None]
    if not vals:
        return False
    numeric = sum(1 for v in vals if isinstance(v, (int, float)))
    return numeric / len(vals) >= 0.7


def _make_title(question: str) -> str:
    q = question.strip().rstrip("?")
    return q[:80] + ("…" if len(q) > 80 else "")
