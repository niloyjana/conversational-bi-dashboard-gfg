from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import os
import sys
from dotenv import load_dotenv
import uvicorn

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from query_processor import QueryProcessor
from chart_selector import ChartSelector

# Look for both .env and backend.env
load_dotenv()
load_dotenv("backend.env")

app = FastAPI(title="Conversational BI Dashboard API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
query_processor = QueryProcessor(api_key=os.getenv("GEMINI_API_KEY"))
chart_selector = ChartSelector(api_key=os.getenv("GEMINI_API_KEY"))

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    sql_query: str
    data: list
    chart_config: dict
    row_count: int
    execution_time: float
    ai_reasoning: dict | None = None
    suggestions: list = []

@app.get("/")
async def root():
    return {"message": "Conversational BI Dashboard API", "status": "running"}

@app.get("/table-info")
async def get_table_info():
    """Get information about the current table"""
    return db_manager.get_table_info()

@app.post("/query", response_model=QueryResponse)
async def process_query_endpoint(request: QueryRequest):
    """Process natural language query and return data + visualization"""
    import time
    start_time = time.time()

    try:
        # Get fresh table info (includes table_name, columns, dtypes)
        table_info = db_manager.get_table_info()
        print(f"[API] /query received: '{request.query}'")
        print(f"[API] Using table: '{table_info.get('table_name')}' with columns: {table_info.get('columns')}")

        # Generate SQL
        query_result = query_processor.generate_sql_query(request.query, table_info)

        if not query_result or not isinstance(query_result, dict):
            raise HTTPException(status_code=400, detail="Failed to generate SQL logic")

        sql_query    = query_result.get("sql_query", "")
        ai_reasoning = query_result.get("reasoning", {})
        suggestions  = query_result.get("suggestions", [])

        # If LLM cannot answer, return graceful response immediately
        if sql_query == "INSUFFICIENT_DATA":
            return QueryResponse(
                sql_query="INSUFFICIENT_DATA",
                data=[],
                chart_config={"type": "none", "title": "Cannot Answer This Query", "data": []},
                row_count=0,
                execution_time=time.time() - start_time,
                ai_reasoning=ai_reasoning,
                suggestions=suggestions,
            )

        print(f"[API] Generated SQL: {sql_query}")

        # Execute query
        result_df = db_manager.execute_query(sql_query)

        if result_df is None or len(result_df) == 0:
            # Self-healing: ask LLM to fix the query
            improved_query = query_processor.validate_and_improve_query(
                request.query, sql_query, "No results returned", table_info
            )
            print(f"[API] Self-healed SQL: {improved_query}")
            result_df = db_manager.execute_query(improved_query)
            sql_query = improved_query

        if result_df is None:
            raise HTTPException(status_code=400, detail="Query execution failed")

        if len(result_df) == 0:
            return QueryResponse(
                sql_query=sql_query,
                data=[],
                chart_config={"type": "table", "title": "No Data Found", "data": []},
                row_count=0,
                execution_time=time.time() - start_time,
                ai_reasoning=ai_reasoning,
            )

        # Select chart type
        chart_config = chart_selector.select_chart(result_df, request.query)

        return QueryResponse(
            sql_query=sql_query,
            data=result_df.to_dict(orient='records'),
            chart_config=chart_config,
            row_count=len(result_df),
            execution_time=time.time() - start_time,
            ai_reasoning=ai_reasoning,
            suggestions=[],
        )

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a new CSV dataset — fully resets schema."""
    try:
        contents = await file.read()
        df = None
        for encoding in ('utf-8', 'utf-8-sig', 'latin-1', 'windows-1252'):
            try:
                df = pd.read_csv(io.StringIO(contents.decode(encoding)))
                print(f"[API] CSV decoded with {encoding} encoding.")
                break
            except (UnicodeDecodeError, Exception):
                continue
        if df is None:
            df = pd.read_csv(io.BytesIO(contents), encoding_errors='replace')
            print("[API] CSV decoded using BytesIO fallback.")

        # Pass filename so database can derive the correct table name
        table_info = db_manager.upload_new_dataset(df, filename=file.filename)
        print(f"[API] Upload complete — table '{table_info.get('table_name')}', columns: {table_info.get('columns')}")

        return {
            "message": "Dataset uploaded successfully",
            "filename": file.filename,
            "table_name": table_info.get("table_name"),
            "rows": len(df),
            "columns": table_info["columns"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/clarify")
async def clarify_query_endpoint(request: QueryRequest):
    """Get clarifying questions for ambiguous queries"""
    try:
        table_info = db_manager.get_table_info()
        questions = query_processor.interpret_ambiguous_query(request.query, table_info)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
