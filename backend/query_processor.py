"""
Convert natural-language questions to SQLite-compatible SQL using Gemini.
"""
import os
import re
import json
import google.generativeai as genai
from database import get_table_info, TABLE_NAME

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-1.5-flash")


def _schema_prompt(info: dict) -> str:
    col_details = info.get("column_details", [])
    col_lines = "\n".join(f"  - {c['name']} ({c['type']})" for c in col_details)
    sample = info.get("sample_rows", [])
    sample_str = json.dumps(sample[:2], indent=2) if sample else "N/A"
    return f"""
You are an expert SQLite query generator for a business intelligence dashboard.

Table name: `{TABLE_NAME}`
Columns:
{col_lines}

Sample rows:
{sample_str}

Rules:
1. ONLY generate SELECT queries compatible with SQLite.
2. For totals/aggregates use SUM(), AVG(), COUNT() with GROUP BY.
3. For time trends, GROUP BY year or month columns.
4. For proportions/breakdowns, return grouped rows.
5. Normalize text comparisons with LOWER() to avoid duplicates.
6. Limit results to 500 rows max using LIMIT 500.
7. Always alias aggregated columns with meaningful names (e.g., SUM(claim_amount) AS total_claim_amount).
8. Return ONLY the raw SQL query — no markdown, no explanation, no code blocks.
"""


def natural_to_sql(question: str) -> str:
    """Convert a natural-language question to a SQL query."""
    info = get_table_info()
    if "error" in info:
        raise ValueError(info["error"])

    schema_ctx = _schema_prompt(info)
    prompt = f"{schema_ctx}\n\nUser question: {question}\n\nSQL query:"

    response = _model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown fences if present
    raw = re.sub(r"```sql\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```\s*", "", raw)
    sql = raw.strip().rstrip(";")

    _validate_sql(sql)
    return sql


def get_clarifying_questions(question: str) -> list[str]:
    """Return clarifying questions for ambiguous queries."""
    info = get_table_info()
    if "error" in info:
        return []

    cols = ", ".join(info.get("columns", []))
    prompt = f"""
You are a BI assistant. A user asked: "{question}"
Available columns: {cols}

Is this question ambiguous or under-specified? If yes, return 1-3 short clarifying questions
as a JSON array of strings. If the question is clear, return an empty array [].
Return ONLY valid JSON — no explanation, no markdown.
"""
    try:
        resp = _model.generate_content(prompt)
        raw = resp.text.strip()
        raw = re.sub(r"```json\s*|```\s*", "", raw)
        questions = json.loads(raw)
        return questions if isinstance(questions, list) else []
    except Exception:
        return []


def _validate_sql(sql: str):
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        raise ValueError(f"Generated query is not a SELECT: {sql[:80]}")
    forbidden = ["DROP ", "DELETE ", "INSERT ", "UPDATE ", "ALTER ", "CREATE ", "TRUNCATE "]
    for kw in forbidden:
        if kw in sql_upper:
            raise ValueError(f"Unsafe keyword '{kw.strip()}' in generated SQL.")