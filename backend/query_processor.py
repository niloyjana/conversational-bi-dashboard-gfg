import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
load_dotenv("backend.env")

# ─────────────────────────────────────────────────────────────────────────────
# Semantic term → column alias map (generic; extended at runtime per dataset)
# ─────────────────────────────────────────────────────────────────────────────
SEMANTIC_MAP = {
    # Generic aggregation aliases
    "total":        "SUM",
    "average":      "AVG",
    "count":        "COUNT",
    "maximum":      "MAX",
    "minimum":      "MIN",
    # Insurance-domain aliases (kept for backwards compatibility)
    "claim amount":                 "claims_paid_amt",
    "claims amount":                "claims_paid_amt",
    "paid amount":                  "claims_paid_amt",
    "settlement ratio":             "claims_paid_ratio_no",
    "claim settlement ratio":       "claims_paid_ratio_no",
    "settled ratio":                "claims_paid_ratio_no",
    "claims paid":                  "claims_paid_no",
    "paid claims":                  "claims_paid_no",
    "repudiated claims":            "claims_repudiated_no",
    "repudiation":                  "claims_repudiated_no",
    "rejected claims":              "claims_rejected_no",
    "rejections":                   "claims_rejected_no",
    "pending claims":               "claims_pending_end_no",
    "total claims":                 "total_claims_no",
    "intimated claims":             "claims_intimated_no",
    "unclaimed":                    "claims_unclaimed_no",
    "pending ratio":                "claims_pending_ratio_no",
    "rejection ratio":              "claims_repudiated_rejected_ratio_no",
    "company":                      "life_insurer",
    "insurer":                      "life_insurer",
    "insurance company":            "life_insurer",
    "provider":                     "life_insurer",
}


def _build_schema_block(table_info: dict) -> str:
    """Build a compact schema description string to inject into LLM prompts."""
    table = table_info.get("table_name", "dataset")
    columns = table_info.get("columns", [])
    dtypes = table_info.get("dtypes", {})
    lines = [f"Table: {table}"]
    lines.append("Columns (name: type):")
    for col in columns:
        dtype = dtypes.get(col, "unknown")
        lines.append(f"  - {col}: {dtype}")
    sample = table_info.get("sample_data", [])
    if sample:
        lines.append(f"Sample row: {json.dumps(sample[0], default=str)}")
    return "\n".join(lines)


def _validate_sql_columns(sql: str, allowed_columns: list, table_name: str = "") -> list:
    """
    Light structural check for obviously hallucinated column references.
    Intentionally lenient to avoid false positives on valid LLM output.
    Strips AS aliases, table names, SQL keywords and common alias words
    before flagging anything.
    """
    SQL_KEYWORDS = {
        "select", "from", "where", "group", "by", "order", "having", "limit",
        "and", "or", "not", "in", "like", "is", "null", "as", "on", "join",
        "inner", "left", "right", "outer", "union", "all", "distinct", "case",
        "when", "then", "else", "end", "sum", "avg", "count", "max", "min",
        "lower", "upper", "trim", "cast", "coalesce", "asc", "desc",
        "collate", "nocase", "between", "exists", "with", "over", "partition",
        "iif", "round", "abs", "length", "substr", "instr", "replace",
        "strftime", "date", "time", "datetime", "values",
    }
    # Common words that appear as column aliases — must NOT be flagged
    COMMON_ALIAS_WORDS = {
        "total", "count", "value", "name", "id", "type", "code", "amount",
        "number", "ratio", "rate", "start", "end", "data", "result", "row",
        "col", "column", "key", "index", "label", "text", "flag", "avg",
        "sum", "max", "min", "paid", "pending", "insurer", "year", "category",
    }

    # Strip string literals
    stripped = re.sub(r"'[^']*'", " __str__ ", sql)
    # Strip numbers
    stripped = re.sub(r"\b\d+(\.\d+)?\b", " __num__ ", stripped)
    # Strip AS alias_name so we don't flag aliases
    stripped = re.sub(r'\bAS\s+(\w+)', ' AS __alias__ ', stripped, flags=re.IGNORECASE)

    tokens = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', stripped)
    allowed_lower = {c.lower() for c in allowed_columns}
    if table_name:
        allowed_lower.add(table_name.lower())

    hallucinated = []
    seen = set()
    for tok in tokens:
        t = tok.lower()
        if t in SQL_KEYWORDS:
            continue
        if t in ('__str__', '__num__', '__alias__'):
            continue
        if t in allowed_lower:
            continue
        if t in COMMON_ALIAS_WORDS:
            continue
        if t in seen:
            continue
        seen.add(t)
        hallucinated.append(tok)

    return hallucinated


class QueryProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment")

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        else:
            self.model = None

    # ── Helper: apply semantic mapping ────────────────────────────────────────
    def _apply_semantic_mapping(self, query: str) -> tuple[str, dict]:
        mapped = query.lower()
        applied = {}
        for term, col in sorted(SEMANTIC_MAP.items(), key=lambda x: -len(x[0])):
            if term in mapped:
                mapped = mapped.replace(term, col)
                applied[term] = col
        return mapped, applied

    # ── Core: Generate SQL ────────────────────────────────────────────────────
    def generate_sql_query(self, natural_query: str, table_info: dict) -> dict:
        """
        3-Stage pipeline:
          1. Semantic mapping
          2. LLM SQL generation with full schema injection
          3. Post-generation column validation
        Returns: {sql_query, reasoning, suggestions}
        """
        if not self.model:
            return {
                "sql_query":   "SELECT * FROM dataset LIMIT 10",
                "reasoning":   {"intent": "fallback_no_api_key"},
                "suggestions": [],
            }

        table_name = table_info.get("table_name", "dataset")
        columns    = table_info.get("columns", [])
        schema_block = _build_schema_block(table_info)

        # Stage 1: semantic mapping
        mapped_query, applied_mappings = self._apply_semantic_mapping(natural_query)

        print(f"[QP] Query: '{natural_query}'")
        print(f"[QP] Mapped: '{mapped_query}'")
        print(f"[QP] Schema passed to LLM:\n{schema_block}")

        # Stage 2: LLM SQL generation
        prompt = f"""You are an expert SQL query generator for a SQLite database.

{schema_block}

User question: "{mapped_query}"

Instructions:
- Use ONLY the table name and column names listed in the schema above. Do NOT invent column names.
- The table name is exactly: {table_name}
- When filtering on text/categorical columns, always use LOWER(column) = LOWER('value') or LIKE '%value%' for case-insensitive matching.
- Use SUM(), AVG(), COUNT(), MAX(), MIN() with GROUP BY for aggregation questions.
- For ranking questions, use ORDER BY ... DESC LIMIT N.
- For time-series or trend questions, GROUP BY the time column and ORDER BY it ASC.
- Do NOT add filters that the user did not ask for (e.g. do not filter by year unless the user mentioned a specific year).
- Alias aggregated columns clearly (e.g. SUM(col) AS total_col).
- If the requested information cannot be answered using only the available columns above, output exactly: INSUFFICIENT_DATA

Follow exactly this format:

Relevant Columns: [comma-separated list from schema]
Can Question Be Answered: YES or NO
SQL Query:
[SQL statement or INSUFFICIENT_DATA]
"""

        try:
            response    = self.model.generate_content(prompt)
            output_text = response.text.strip()

            columns_match    = re.search(
                r'Relevant Columns\s*:\s*(.*?)(?=Can Question|$)',
                output_text, re.DOTALL | re.IGNORECASE)
            answerable_match = re.search(
                r'Can Question Be Answered\s*:\s*(YES|NO)',
                output_text, re.IGNORECASE)
            sql_match        = re.search(
                r'SQL Query\s*:\s*([\s\S]+)',
                output_text, re.IGNORECASE)

            relevant_columns = columns_match.group(1).strip()  if columns_match    else "Unknown"
            is_answerable    = (answerable_match.group(1).upper() == "YES") if answerable_match else False

            sql = "INSUFFICIENT_DATA"
            if sql_match:
                raw_sql = sql_match.group(1).strip()
                raw_sql = re.sub(r'```sql\s*|```', '', raw_sql).strip()
                # Take only lines that look like SQL
                sql_lines = []
                for line in raw_sql.splitlines():
                    s = line.strip()
                    if not s:
                        if sql_lines:
                            break  # stop at first blank line after SQL started
                        continue
                    if s.lower().startswith(('note:', 'explanation', 'this query', '--')):
                        if sql_lines:
                            break
                        continue
                    sql_lines.append(line)
                sql = '\n'.join(sql_lines).strip()

            if not is_answerable or not sql or 'INSUFFICIENT_DATA' in sql.upper():
                sql = "INSUFFICIENT_DATA"

            # Stage 3: post-generation column validation
            if sql != "INSUFFICIENT_DATA":
                bad_cols = _validate_sql_columns(sql, columns, table_name=table_name)
                if bad_cols:
                    print(f"[QP] Column check: hallucinated identifiers found: {bad_cols} — blocking SQL.")
                    sql = "INSUFFICIENT_DATA"
                    is_answerable = False

            return {
                "sql_query": sql,
                "reasoning": {
                    "relevant_columns":  relevant_columns,
                    "applied_mappings":  applied_mappings,
                    "is_answerable":     is_answerable,
                    "table_name":        table_name,
                },
                "suggestions": self._build_suggestions(table_info) if not is_answerable else [],
            }

        except Exception as e:
            print(f"[QP] Error generating SQL: {e}")
            return {
                "sql_query":   "INSUFFICIENT_DATA",
                "reasoning":   {"error": str(e)},
                "suggestions": self._build_suggestions(table_info),
            }

    # ── Self-healing: validate and improve ────────────────────────────────────
    def validate_and_improve_query(self, natural_query: str, sql_query: str,
                                   error: str | None, table_info: dict) -> str:
        """Re-ask the LLM to fix a broken SQL query, with schema context."""
        if not self.model:
            return sql_query

        schema_block = _build_schema_block(table_info)
        if error:
            prompt = f"""The following SQL query generated an error. Fix it.

{schema_block}

Original natural language query: "{natural_query}"
Faulty SQL: {sql_query}
Error: {error}

Return ONLY the corrected SQLite SQL query, no explanations:"""
        else:
            prompt = f"""Validate and improve this SQLite SQL query if necessary.

{schema_block}

Original query: "{natural_query}"
SQL: {sql_query}

Return ONLY the SQL:"""

        try:
            response = self.model.generate_content(prompt)
            improved = re.sub(r'```sql\s*|```', '', response.text).strip()
            return improved
        except Exception as e:
            print(f"[QP] Error validating query: {e}")
            return sql_query

    # ── Ambiguity detection ────────────────────────────────────────────────────
    def interpret_ambiguous_query(self, natural_query: str, table_info: dict) -> list[str]:
        """Return clarifying questions for genuinely ambiguous queries."""
        if not self.model:
            return []

        schema_block = _build_schema_block(table_info)
        prompt = f"""You are a data analyst assistant.

{schema_block}

A user asked: "{natural_query}"

Is this query clear enough to translate into SQL using the schema above?
- If YES and you can determine intent, return an empty JSON list: []
- If NO and it is genuinely ambiguous, return 1-2 short clarifying questions as a JSON list.

Return ONLY valid JSON (no markdown). Examples: [] or ["Which year?", "Which insurer?"]"""

        try:
            response = self.model.generate_content(prompt)
            clean    = re.sub(r'```json\s*|```', '', response.text).strip()
            questions = json.loads(clean)
            return questions if isinstance(questions, list) else []
        except Exception as e:
            print(f"[QP] Error interpreting query: {e}")
            return []

    # ── Utility: build dynamic suggestions ────────────────────────────────────
    def _build_suggestions(self, table_info: dict) -> list[str]:
        """Generate example queries based on the actual columns available."""
        cols  = table_info.get("columns", [])
        table = table_info.get("table_name", "dataset")
        dtypes = table_info.get("dtypes", {})

        numeric_cols     = [c for c, t in dtypes.items() if 'int' in t or 'float' in t]
        categorical_cols = [c for c, t in dtypes.items() if 'object' in t or 'str' in t]
        date_cols        = [c for c, t in dtypes.items() if 'date' in t.lower() or c.lower() in ('year', 'date', 'month')]

        suggestions = []
        if numeric_cols and categorical_cols:
            suggestions.append(f"Show total {numeric_cols[0]} by {categorical_cols[0]}")
            suggestions.append(f"Average {numeric_cols[0]} by {categorical_cols[0]}")
        if numeric_cols:
            suggestions.append(f"Top 10 rows by {numeric_cols[0]}")
        if date_cols and numeric_cols:
            suggestions.append(f"Trend of {numeric_cols[0]} over {date_cols[0]}")
        if categorical_cols:
            suggestions.append(f"Count of records by {categorical_cols[0]}")

        return suggestions[:5]
