# 📊 Conversational BI Dashboard

A powerful, AI-driven Business Intelligence dashboard that allows users to analyze data using natural language. Built with **FastAPI**, **Streamlit**, and **Google Gemini AI**, it transforms plain English questions into optimized SQL queries, executes them against a database, and automatically selects the most appropriate visualization.

![Main Dashboard Preview](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Backend API](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![AI Engine](https://img.shields.io/badge/AI-Gemini-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

## 🚀 Key Features

- **Natural Language to SQL**: Ask complex analytical questions in plain English (e.g., *"Show the trend of claims over the last 3 years"*).
- **Automated Visualization**: Smart chart selection that chooses between Bar, Line, Pie, and Scatter plots based on the data structure.
- **Dynamic Dataset Upload**: Upload any CSV file and start asking questions immediately.
- **Conversational Refinement**: The AI asks follow-up questions if your query is ambiguous.
- **Query History**: Keep track of your previous insights and re-run them with a single click.
- **Performance Metrics**: View row counts, execution times, and generated SQL for full transparency.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) – Interactive web interface.
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) – High-performance Python API.
- **LLM Engine**: [Google Gemini AI](https://ai.google.dev/) – Advanced natural language understanding.
- **Visualization**: [Plotly](https://plotly.com/python/) – Dynamic, interactive charts.
- **Database Engine**: [SQLite](https://www.sqlite.org/) / [SQLAlchemy](https://www.sqlalchemy.org/) – Lightweight and efficient data storage.

## 📂 Project Structure

```text
cbidashboard/
├── backend/
│   ├── app.py              # FastAPI main entry point
│   ├── query_processor.py  # Gemini LLM integration for SQL generation
│   ├── database.py         # Database connection and CRUD operations
│   ├── chart_selector.py   # Logic for automatic chart type selection
│   └── data/               # Directory for stored SQLite DB and uploaded CSVs
├── frontend/
│   └── app (1).py          # Streamlit dashboard interface
└── README.md               # Project documentation
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.9+
- A Google Gemini API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/cbidashboard.git
   cd cbidashboard
   ```

2. **Set up the Backend**:
   ```bash
   cd backend
   # Create a virtual environment and install dependencies
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set your Gemini API Key in .env or environment variables
   # export GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Set up the Frontend**:
   ```bash
   cd ../frontend
   # Install frontend dependencies
   pip install streamlit pandas plotly requests
   ```

### Running the Application

1. **Start the FastAPI Backend**:
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

2. **Start the Streamlit Frontend**:
   ```bash
   cd frontend
   streamlit run "app (1).py"
   ```

3. **Open the Dashboard**:
   Navigate to `http://localhost:8501` in your browser.

## 💡 Example Queries

- *"Show total claim amount by insurer"*
- *"What is the average claim amount per state?"*
- *"Show me a breakdown of claim status by policy type"*
- *"List the top 10 states by total claim amount"*

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
