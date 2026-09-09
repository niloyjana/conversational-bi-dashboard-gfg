# 📊 Conversational BI Dashboard

An AI-powered Business Intelligence dashboard that lets you query a database using plain English. Ask a question, and it converts your words into SQL, runs the query, and automatically picks the right chart to visualize the result — no SQL or dashboard-building knowledge required.

Built with **FastAPI**, **Streamlit**, and **Google Gemini**.

![UI](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Backend](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![AI Engine](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

## 🚀 Key Features

- **Natural Language → SQL**: Ask questions like *"Show the trend of claims over the last 3 years"* and get a valid, safe SQL query back.
- **Automatic Chart Selection**: Rule-based engine picks between Line, Pie, Scatter, Bar, or a plain table depending on the shape of the result and the intent of your question (trend, breakdown, correlation, comparison).
- **Query Safety Guardrails**: Only `SELECT` statements are allowed — the backend rejects any generated query containing `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`, or `TRUNCATE`.
- **Dynamic Dataset Upload**: Upload any CSV via the `/upload` endpoint; column names are auto-normalized and loaded into SQLite on the fly.
- **Clarifying Questions**: For ambiguous prompts, the AI can propose follow-up questions before running a query.
- **Full Transparency**: Every response includes the generated SQL, row count, execution time, and returned columns.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) |
| LLM Engine | [Google Gemini 1.5 Flash](https://ai.google.dev/) |
| Visualization | [Plotly](https://plotly.com/python/) |
| Data Layer | SQLite + [pandas](https://pandas.pydata.org/) |

## 📂 Project Structure

```text
conversational-bi-dashboard-gfg/
├── backend/
│   ├── app.py               # FastAPI entry point & routes
│   ├── query_processor.py   # Gemini-powered NL → SQL + clarifying questions
│   ├── database.py          # SQLite connection, CSV loading, query execution
│   ├── chart_selector.py    # Rule-based chart type selection
│   ├── .env.example         # Environment variable template
│   └── data/                # SQLite DB + uploaded/default CSVs (gitignored)
└── frontend/
    └── app (1).py           # Streamlit dashboard UI
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://ai.google.dev/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/niloyjana/conversational-bi-dashboard-gfg.git
   cd conversational-bi-dashboard-gfg
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   cp .env.example .env
   # then edit .env and add your key:
   # GOOGLE_API_KEY=your_api_key_here
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   pip install streamlit pandas plotly requests
   ```

### Running the App

1. **Start the FastAPI backend**
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run "app (1).py"
   ```

3. Open **http://localhost:8501** in your browser.

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/table-info` | Returns current table schema, column types, and sample rows |
| `POST` | `/query` | Converts a natural-language question to SQL, executes it, and returns data + chart config |
| `POST` | `/clarify` | Returns clarifying questions for an ambiguous query, if any |
| `POST` | `/upload` | Upload a CSV file to replace the active dataset |

## 💡 Example Queries

- *"Show total claim amount by insurer"*
- *"What is the average claim amount per state?"*
- *"Show me a breakdown of claim status by policy type"*
- *"List the top 10 states by total claim amount"*
- *"Show the trend of claims over the last 3 years"*

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
