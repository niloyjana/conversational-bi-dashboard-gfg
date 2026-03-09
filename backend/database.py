import pandas as pd
import sqlite3
import os
import re
from pathlib import Path


def _slugify_table_name(filename: str) -> str:
    """Convert a CSV filename into a valid SQLite table name."""
    base = Path(filename).stem
    slug = re.sub(r'[^a-zA-Z0-9]', '_', base).lower().strip('_')
    # Ensure it starts with a letter
    if slug and slug[0].isdigit():
        slug = 't_' + slug
    return slug or 'dataset'


class DatabaseManager:
    def __init__(self, csv_path=None):
        self.conn = None
        self.df = None
        self.table_name = 'dataset'  # will be set dynamically

        # Locate default CSV
        data_dir = os.path.join(Path(__file__).parent.parent, 'data')
        default_csv = None

        if csv_path:
            default_csv = csv_path
        elif os.path.isdir(data_dir):
            csv_files = sorted([
                os.path.join(data_dir, f)
                for f in os.listdir(data_dir)
                if f.lower().endswith('.csv')
            ])
            if csv_files:
                default_csv = csv_files[0]

        self.csv_path = default_csv
        if self.csv_path:
            self.setup_database(self.csv_path)
        else:
            print("Warning: No CSV file found to load on startup.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_csv(self, path: str) -> pd.DataFrame | None:
        """Try multiple encodings and return a DataFrame, or None on failure."""
        for encoding in ('utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'ISO-8859-1'):
            try:
                df = pd.read_csv(path, encoding=encoding)
                print(f"[DB] Loaded CSV '{os.path.basename(path)}' with {encoding} encoding.")
                return df
            except UnicodeDecodeError:
                continue
        # Last resort
        try:
            df = pd.read_csv(path, encoding_errors='replace')
            print(f"[DB] Loaded CSV '{os.path.basename(path)}' with replace-error fallback.")
            return df
        except Exception as e:
            print(f"[DB] ERROR loading CSV: {e}")
            return None

    def _sanitize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip and normalize column names to safe SQL identifiers."""
        df = df.copy()
        df.columns = [
            re.sub(r'[^a-zA-Z0-9]', '_', col.strip()).strip('_').lower()
            for col in df.columns
        ]
        # Deduplicate column names
        seen = {}
        new_cols = []
        for col in df.columns:
            if col in seen:
                seen[col] += 1
                new_cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                new_cols.append(col)
        df.columns = new_cols
        return df

    def _write_to_sqlite(self, df: pd.DataFrame, table_name: str):
        """(Re)create the in-memory SQLite DB and write the dataframe."""
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        df.to_sql(table_name, self.conn, index=False, if_exists='replace')
        print(f"[DB] SQLite table '{table_name}' created with {len(df)} rows.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def setup_database(self, csv_path: str) -> bool:
        """Load a CSV file and set up the in-memory SQLite database."""
        df = self._load_csv(csv_path)
        if df is None:
            return False

        df = self._sanitize_columns(df)
        self.table_name = _slugify_table_name(csv_path)
        self._write_to_sqlite(df, self.table_name)
        self.df = df
        self.csv_path = csv_path

        schema_summary = ', '.join(
            f"{col}({dtype})" for col, dtype in zip(df.columns, df.dtypes)
        )
        print(f"[SCHEMA] Table: {self.table_name} | Columns: {schema_summary}")
        return True

    def upload_new_dataset(self, df: pd.DataFrame, filename: str = 'uploaded.csv') -> dict:
        """Replace the current dataset with a new one (full reset, no cache)."""
        df = self._sanitize_columns(df)
        self.table_name = _slugify_table_name(filename)
        self._write_to_sqlite(df, self.table_name)
        self.df = df
        self.csv_path = filename

        schema_summary = ', '.join(
            f"{col}({dtype})" for col, dtype in zip(df.columns, df.dtypes)
        )
        print(f"[SCHEMA] Reloaded — Table: {self.table_name} | Columns: {schema_summary}")
        return self.get_table_info()

    def execute_query(self, query: str) -> pd.DataFrame | None:
        """Execute a SQL query and return results as a DataFrame."""
        if not self.conn:
            print("[DB] ERROR: No database connection.")
            return None
        try:
            result_df = pd.read_sql_query(query, self.conn)
            return result_df
        except Exception as e:
            print(f"[DB] Query execution error: {e}")
            return None

    def get_table_info(self) -> dict:
        """Return the current schema info for use in prompts and the API."""
        if self.df is None or not self.conn:
            return {'error': 'Database not initialized', 'table_name': self.table_name}

        sample = self.df.head(3).to_dict(orient='records')
        dtypes = {col: str(dtype) for col, dtype in zip(self.df.columns, self.df.dtypes)}

        info = {
            'table_name': self.table_name,
            'columns': list(self.df.columns),
            'dtypes': dtypes,
            'row_count': len(self.df),
            'sample_data': sample,
        }
        # Log on every access so we can confirm the right schema is in use
        print(f"[SCHEMA] Table: {self.table_name} | Columns: {list(self.df.columns)}")
        return info

    def get_dataframe(self) -> pd.DataFrame | None:
        return self.df
