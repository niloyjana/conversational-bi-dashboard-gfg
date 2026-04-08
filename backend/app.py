"""
FastAPI backend for the Conversational BI Dashboard.
"""
import os
import shutil
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import database as db
import query_processor as qp
import chart_selector as cs

app = FastAPI(title="Conversational BI Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str

class ClarifyRequest(BaseModel):
    query: str


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Conversational BI Dashboard API"}


@app.get("/table-info")
def table_info():
    info = db.get_table_info()
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    return info


@app.post("/query")
def process_query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Convert NL → SQL
    try:
        sql = qp.natural_to_sql(req.query)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"SQL generation failed: {e}")

    # 2. Execute SQL
    result = db.execute_query(sql)
    if "error" in result and result["data"] == []:
        raise HTTPException(status_code=500, detail=result["error"])

    # 3. Select chart type
    chart_config = cs.select_chart(result["data"], sql, req.query)
    chart_config["data"] = result["data"]

    return {
        "sql_query": sql,
        "chart_config": chart_config,
        "data": result["data"],
        "row_count": result["row_count"],
        "execution_time": result.get("execution_time", 0),
        "columns": result.get("columns", []),
    }


@app.post("/clarify")
def clarify(req: ClarifyRequest):
    questions = qp.get_clarifying_questions(req.query)
    return {"questions": questions}


@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Save to a temp file then move to data dir
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    dest_path = os.path.join(data_dir, "uploaded_dataset.csv")

    with open(dest_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        info = db.load_csv_to_db(csv_path=dest_path)
        return {"message": "Dataset uploaded successfully.", "info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dataset: {e}")
