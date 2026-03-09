# Conversational BI Dashboard

This project is a conversational Business Intelligence (BI) dashboard that allows users to query data using natural language and visualize the results using Google's Gemini AI.

## Project Structure

- `backend/`: FastAPI server that handles natural language processing, SQL generation, and data fetching.
- `frontend/`: Streamlit application for the user interface and visualizations.
- `data/`: Contains the insurance claims dataset.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key (get one at [aistudio.google.com](https://aistudio.google.com/))

### 2. Configure Environment
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Install Dependencies
Open two terminals.

**Terminal 1 (Backend):**
```bash
cd backend
pip install -r requirements.txt
```

**Terminal 2 (Frontend):**
```bash
cd frontend
pip install -r requirements.txt
```

### 4. Run the Application

**Run Backend:**
```bash
cd backend
python app.py
```
The API will run on `http://localhost:8000`.

**Run Frontend:**
```bash
cd frontend
streamlit run app.py
```
The dashboard will open in your browser at `http://localhost:8501`.

## Features
- **Natural Language Input**: Ask questions like "Show me total claims by state".
- **AI-Powered SQL**: Automatically generates the correct SQL query for your data.
- **Smart Visualization**: Automatically selects the best chart type (Bar, Line, Pie, etc.).
- **Ambiguity Handling**: Asks clarifying questions if the query is unclear.
- **Custom Uploads**: Upload your own CSV files to analyze them instantly.
