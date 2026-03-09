import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Conversational BI Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS — Glossy Glassmorphism Blue Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    /* ══════════════════════════════════════════
       GLOBAL
    ══════════════════════════════════════════ */
    html, body, [class*="css"], .stApp {
        font-family: 'DM Sans', sans-serif;
        background: #03091a !important;
    }

    .stApp {
        background:
            radial-gradient(ellipse 90% 55% at 15%  5%,  rgba(0,110,255,0.22) 0%, transparent 58%),
            radial-gradient(ellipse 65% 45% at 85% 85%,  rgba(0,195,255,0.14) 0%, transparent 52%),
            radial-gradient(ellipse 50% 60% at 55% 45%,  rgba(5, 30, 80,0.45) 0%, transparent 65%),
            linear-gradient(155deg, #03091a 0%, #061830 55%, #030d1f 100%) !important;
        background-attachment: fixed !important;
    }

    /* subtle grain */
    .stApp::before {
        content: '';
        position: fixed; inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
        pointer-events: none; z-index: 0; opacity: 0.6;
    }

    /* ══════════════════════════════════════════
       TYPOGRAPHY
    ══════════════════════════════════════════ */
    h1,h2,h3,h4,h5,h6,.main-header,.sub-header { font-family:'Syne',sans-serif !important; }

    .main-header {
        font-size: 2.6rem; font-weight: 800; text-align: center;
        margin-bottom: 0.3rem; letter-spacing: -0.5px;
        background: linear-gradient(130deg, #ffffff 0%, #a8d8ff 30%, #3ab0ff 65%, #0060ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        filter: drop-shadow(0 0 28px rgba(0,140,255,0.45));
    }

    .sub-header {
        font-size: 0.92rem; font-weight: 300; letter-spacing: 0.6px;
        color: rgba(140,195,255,0.65); text-align: center; margin-bottom: 2rem;
    }

    /* ══════════════════════════════════════════
       SIDEBAR — compact & polished
    ══════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(160deg,
                rgba(4,18,50,0.97) 0%,
                rgba(2,12,38,0.99) 100%),
            url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E") !important;
        border-right: 1px solid rgba(0,130,255,0.18) !important;
        backdrop-filter: blur(24px) !important;
        box-shadow: 4px 0 30px rgba(0,40,120,0.3) !important;
    }

    /* sidebar inner padding tighter */
    [data-testid="stSidebar"] > div:first-child { padding: 0.9rem 0.8rem !important; }

    /* all sidebar text — small & crisp */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stText,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        font-size: 0.72rem !important;
        color: rgba(160, 210, 255, 0.75) !important;
        line-height: 1.5 !important;
    }

    [data-testid="stSidebar"] h1 { font-size: 0.95rem !important; color: #4cc8ff !important; margin-bottom: 0.2rem !important; }
    [data-testid="stSidebar"] h2 { font-size: 0.82rem !important; color: #4cc8ff !important; margin-bottom: 0.15rem !important; }
    [data-testid="stSidebar"] h3 { font-size: 0.78rem !important; color: #4cc8ff !important; margin-bottom: 0.1rem !important; }

    [data-testid="stSidebar"] hr {
        border: none !important; height: 1px !important; margin: 0.55rem 0 !important;
        background: linear-gradient(90deg, transparent, rgba(0,130,255,0.3), transparent) !important;
    }

    /* sidebar file uploader — compact */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(0,35,90,0.35) !important;
        border: 1px dashed rgba(0,130,255,0.3) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] * { font-size: 0.7rem !important; }

    /* sidebar buttons — slim */
    [data-testid="stSidebar"] .stButton > button {
        font-size: 0.72rem !important;
        padding: 0.3rem 0.7rem !important;
        height: auto !important;
        border-radius: 7px !important;
    }

    /* sidebar expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        font-size: 0.72rem !important;
        padding: 0.35rem 0.6rem !important;
        border-radius: 7px !important;
    }

    /* ══════════════════════════════════════════
       TEXT INPUT — glossy
    ══════════════════════════════════════════ */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg,
            rgba(0,50,120,0.45) 0%,
            rgba(0,30,80,0.55) 100%) !important;
        border: 1px solid rgba(0,155,255,0.32) !important;
        border-radius: 12px !important;
        color: #d5ecff !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.93rem !important;
        padding: 0.7rem 1rem !important;
        backdrop-filter: blur(12px);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), inset 0 -1px 0 rgba(0,0,0,0.15) !important;
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(100,160,220,0.45) !important; }
    .stTextInput > div > div > input:focus {
        border-color: rgba(0,185,255,0.65) !important;
        box-shadow: 0 0 0 3px rgba(0,140,255,0.13), inset 0 1px 0 rgba(255,255,255,0.1), 0 0 18px rgba(0,140,255,0.08) !important;
    }
    .stTextInput label { color: rgba(130,195,255,0.75) !important; font-size: 0.8rem !important; font-weight:500 !important; letter-spacing:0.3px; }

    /* ══════════════════════════════════════════
       BUTTONS — glossy pill style
    ══════════════════════════════════════════ */
    .stButton > button {
        background: linear-gradient(170deg,
            rgba(0,110,230,0.55) 0%,
            rgba(0,55,160,0.7) 100%) !important;
        border: 1px solid rgba(0,165,255,0.38) !important;
        border-radius: 9px !important;
        color: #cce8ff !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px;
        backdrop-filter: blur(12px);
        transition: all 0.22s ease !important;
        box-shadow:
            0 2px 12px rgba(0,80,200,0.2),
            inset 0 1px 0 rgba(255,255,255,0.14),
            inset 0 -1px 0 rgba(0,0,0,0.18) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(170deg, rgba(0,145,255,0.65), rgba(0,80,200,0.78)) !important;
        border-color: rgba(0,200,255,0.55) !important;
        box-shadow: 0 5px 22px rgba(0,120,255,0.38),
                    inset 0 1px 0 rgba(255,255,255,0.18),
                    0 0 18px rgba(0,160,255,0.12) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(150deg, #1a7fff 0%, #0050dd 100%) !important;
        border-color: rgba(0,160,255,0.55) !important;
        box-shadow: 0 4px 18px rgba(0,100,255,0.42),
                    inset 0 1px 0 rgba(255,255,255,0.22),
                    inset 0 -2px 0 rgba(0,0,0,0.2) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(150deg, #3d9bff 0%, #0062f5 100%) !important;
        box-shadow: 0 7px 28px rgba(0,130,255,0.52),
                    0 0 35px rgba(0,160,255,0.18),
                    inset 0 1px 0 rgba(255,255,255,0.24) !important;
    }

    /* ══════════════════════════════════════════
       METRICS — glossy card
    ══════════════════════════════════════════ */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg,
            rgba(255,255,255,0.06) 0%,
            rgba(0,90,200,0.18) 50%,
            rgba(0,40,110,0.28) 100%) !important;
        border: 1px solid rgba(0,145,255,0.22) !important;
        border-radius: 14px !important;
        padding: 1.1rem 1.3rem !important;
        backdrop-filter: blur(18px) !important;
        box-shadow:
            0 4px 22px rgba(0,55,180,0.18),
            inset 0 1px 0 rgba(255,255,255,0.12),
            inset 0 -1px 0 rgba(0,0,0,0.12) !important;
        position: relative; overflow: hidden;
    }
    [data-testid="metric-container"]::before {
        content: ''; position: absolute; top:0; left:0; right:0; height:1px;
        background: linear-gradient(90deg, transparent, rgba(0,195,255,0.55), transparent);
    }
    [data-testid="metric-container"]::after {
        content: ''; position: absolute; top:0; left:0; width:100%; height:40%;
        background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, transparent 100%);
        border-radius: 14px 14px 0 0; pointer-events:none;
    }
    [data-testid="metric-container"] label {
        color: rgba(110,185,255,0.7) !important;
        font-size: 0.72rem !important; font-weight:500 !important;
        text-transform: uppercase; letter-spacing: 0.9px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e8f5ff !important; font-family:'Syne',sans-serif !important;
        font-weight:700 !important; font-size:1.55rem !important;
    }

    /* ══════════════════════════════════════════
       CHARTS
    ══════════════════════════════════════════ */
    .js-plotly-plot, .stPlotlyChart {
        border-radius: 16px !important;
        border: 1px solid rgba(0,125,255,0.18) !important;
        overflow: hidden;
        background: linear-gradient(145deg, rgba(0,15,50,0.55), rgba(0,25,70,0.4)) !important;
        backdrop-filter: blur(12px);
        box-shadow:
            0 8px 36px rgba(0,35,120,0.28),
            inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }

    /* ══════════════════════════════════════════
       EXPANDERS
    ══════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(0,55,130,0.32), rgba(0,35,90,0.28)) !important;
        border: 1px solid rgba(0,120,255,0.18) !important;
        border-radius: 10px !important;
        color: rgba(135,200,255,0.88) !important;
        font-size: 0.82rem !important; font-weight:500 !important;
        backdrop-filter: blur(10px);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.07) !important;
    }
    .streamlit-expanderContent {
        background: rgba(0,15,55,0.32) !important;
        border: 1px solid rgba(0,100,220,0.13) !important;
        border-top: none !important; border-radius: 0 0 10px 10px !important;
    }

    /* ══════════════════════════════════════════
       ALERTS
    ══════════════════════════════════════════ */
    .stAlert { border-radius: 12px !important; backdrop-filter: blur(10px) !important; border-width: 1px !important; }
    div[data-baseweb="notification"] { border-radius: 12px !important; }
    .stInfo    { background: rgba(0,75,175,0.18) !important; border-color: rgba(0,150,255,0.38) !important; color: #b8dcff !important; }
    .stSuccess { background: rgba(0,115,75,0.18) !important; border-color: rgba(0,215,145,0.38) !important; }
    .stError   { background: rgba(175,18,38,0.18) !important; border-color: rgba(255,75,95,0.38) !important; }

    /* ══════════════════════════════════════════
       CODE / DATAFRAME / JSON
    ══════════════════════════════════════════ */
    .stCode, code, pre {
        background: rgba(0,15,55,0.65) !important;
        border: 1px solid rgba(0,100,220,0.22) !important;
        border-radius: 8px !important; color: #78ccff !important; font-size: 0.8rem !important;
    }
    .stDataFrame {
        border: 1px solid rgba(0,115,255,0.18) !important;
        border-radius: 12px !important; overflow: hidden !important;
        backdrop-filter: blur(10px) !important;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] { background: rgba(0,18,55,0.4) !important; }
    .stJson { background: rgba(0,15,55,0.5) !important; border: 1px solid rgba(0,95,200,0.18) !important; border-radius: 10px !important; }

    /* ══════════════════════════════════════════
       MISC
    ══════════════════════════════════════════ */
    hr { border:none !important; height:1px !important; margin:1.4rem 0 !important;
         background: linear-gradient(90deg, transparent, rgba(0,140,255,0.3), transparent) !important; }

    h2, h3, .stSubheader { color: #78ccff !important; font-family:'Syne',sans-serif !important; font-weight:600 !important; }

    .stCaption, caption, small { color: rgba(95,155,215,0.68) !important; font-size:0.74rem !important; }

    p, li, .stMarkdown { color: rgba(175,218,255,0.82) !important; }

    [data-testid="stFileUploader"] {
        background: rgba(0,38,95,0.28) !important;
        border: 1px dashed rgba(0,140,255,0.32) !important;
        border-radius: 12px !important; padding: 0.9rem !important;
    }

    .stSpinner > div > div { border-top-color: #0088ff !important; }

    ::-webkit-scrollbar { width:5px; height:5px; }
    ::-webkit-scrollbar-track { background: rgba(0,8,25,0.5); }
    ::-webkit-scrollbar-thumb { background: rgba(0,95,215,0.42); border-radius:3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,140,255,0.6); }

    /* ══════════════════════════════════════════
       QUERY SECTION CARD
    ══════════════════════════════════════════ */
    .query-section {
        background: linear-gradient(140deg,
            rgba(255,255,255,0.055) 0%,
            rgba(0,90,195,0.14) 45%,
            rgba(0,35,95,0.22) 100%);
        border: 1px solid rgba(0,145,255,0.2);
        border-radius: 18px;
        padding: 1.4rem 1.7rem;
        margin-bottom: 1.4rem;
        backdrop-filter: blur(22px);
        box-shadow:
            0 8px 34px rgba(0,35,135,0.22),
            inset 0 1px 0 rgba(255,255,255,0.1),
            inset 0 -1px 0 rgba(0,0,0,0.1);
        position: relative; overflow: hidden;
    }
    .query-section::before {
        content: ''; position: absolute; top:0; left:0; right:0; height:1px;
        background: linear-gradient(90deg, transparent, rgba(0,195,255,0.62), transparent);
    }
    /* glossy top sheen */
    .query-section::after {
        content: ''; position: absolute; top:0; left:0; width:100%; height:45%;
        background: linear-gradient(180deg, rgba(255,255,255,0.045) 0%, transparent 100%);
        pointer-events: none;
    }

    /* ══════════════════════════════════════════
       CHAT / HISTORY
    ══════════════════════════════════════════ */
    .chat-card {
        background: linear-gradient(135deg, rgba(0,48,115,0.28), rgba(0,28,75,0.33));
        border: 1px solid rgba(0,118,255,0.16);
        border-radius: 12px; padding: 0.8rem 1.1rem; margin-bottom: 0.5rem;
        backdrop-filter: blur(14px);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .chat-card:hover { border-color:rgba(0,158,255,0.32); box-shadow:0 4px 18px rgba(0,75,200,0.18); }

    /* ══════════════════════════════════════════
       PULSE DOT + BADGE
    ══════════════════════════════════════════ */
    .pulse-dot {
        display:inline-block; width:7px; height:7px; background:#00d4ff;
        border-radius:50%; margin-right:6px;
        animation: pulse 2.2s infinite;
        box-shadow: 0 0 0 0 rgba(0,212,255,0.4);
    }
    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0   rgba(0,212,255,0.4); }
        70%  { box-shadow: 0 0 0 7px rgba(0,212,255,0);   }
        100% { box-shadow: 0 0 0 0   rgba(0,212,255,0);   }
    }

    .badge {
        display:inline-block;
        background: rgba(0,95,215,0.32);
        border: 1px solid rgba(0,158,255,0.28);
        border-radius: 20px; padding: 2px 9px;
        font-size: 0.68rem; color: #78ccff;
        letter-spacing: 0.5px; font-weight:500;
    }

    /* ══════════════════════════════════════════
       SIDEBAR NAV ITEM rows
    ══════════════════════════════════════════ */
    .sidebar-item {
        display: flex; align-items: center; gap: 7px;
        background: rgba(0,55,130,0.22);
        border: 1px solid rgba(0,120,255,0.14);
        border-radius: 7px; padding: 5px 9px; margin-bottom: 4px;
        cursor: default;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .sidebar-item .icon { font-size: 0.78rem; }
    .sidebar-item .text { font-size: 0.7rem !important; color: rgba(155,208,255,0.8) !important; }

    .sidebar-section-title {
        font-size: 0.62rem !important; font-weight:600 !important;
        text-transform: uppercase; letter-spacing: 1px;
        color: rgba(80,160,255,0.55) !important;
        margin: 0.6rem 0 0.3rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'current_chart' not in st.session_state:
    st.session_state.current_chart = None
if 'sql_query' not in st.session_state:
    st.session_state.sql_query = None
if 'table_info' not in st.session_state:
    st.session_state.table_info = None
if 'clarifying_questions' not in st.session_state:
    st.session_state.clarifying_questions = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'current_reasoning' not in st.session_state:
    st.session_state.current_reasoning = None
if 'current_suggestions' not in st.session_state:
    st.session_state.current_suggestions = []

def fetch_table_info():
    try:
        response = requests.get(f"{API_URL}/table-info")
        if response.status_code == 200:
            st.session_state.table_info = response.json()
    except:
        pass

def process_query_func(natural_query):
    with st.spinner("🧠 Generating insights..."):
        try:
            response = requests.post(f"{API_URL}/query", json={"query": natural_query})
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            return None

def get_clarifying_questions(query):
    try:
        response = requests.post(f"{API_URL}/clarify", json={"query": query})
        if response.status_code == 200:
            return response.json().get("questions", [])
    except:
        pass
    return None

def upload_file(file):
    with st.spinner("Uploading dataset..."):
        try:
            files = {"file": (file.name, file, "text/csv")}
            response = requests.post(f"{API_URL}/upload", files=files)
            if response.status_code == 200:
                st.success("✅ Dataset uploaded successfully!")
                fetch_table_info()
                return True
            else:
                st.error(f"Upload failed: {response.text}")
                return False
        except Exception as e:
            st.error(f"Upload failed: {e}")
            return False

def render_chart(chart_config):
    if not chart_config or "data" not in chart_config or not chart_config["data"]:
        st.warning("No data to visualize")
        return

    chart_type = chart_config.get("type", "table")
    data = chart_config.get("data", [])
    df = pd.DataFrame(data)

    # Shared Plotly layout for glass theme
    glass_layout = dict(
        paper_bgcolor='rgba(0,15,45,0.0)',
        plot_bgcolor='rgba(0,15,45,0.0)',
        font=dict(color='rgba(180,220,255,0.85)', family='DM Sans'),
        title_font=dict(color='#80ccff', family='Syne', size=16),
        legend=dict(
            bgcolor='rgba(0,30,80,0.5)',
            bordercolor='rgba(0,120,255,0.25)',
            borderwidth=1,
            font=dict(color='rgba(160,210,255,0.8)')
        ),
        xaxis=dict(
            gridcolor='rgba(0,100,200,0.12)',
            linecolor='rgba(0,100,200,0.2)',
            tickfont=dict(color='rgba(140,190,255,0.7)'),
            zerolinecolor='rgba(0,100,200,0.15)'
        ),
        yaxis=dict(
            gridcolor='rgba(0,100,200,0.12)',
            linecolor='rgba(0,100,200,0.2)',
            tickfont=dict(color='rgba(140,190,255,0.7)'),
            zerolinecolor='rgba(0,100,200,0.15)'
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )

    # Blue glass color palette
    blue_palette = [
        '#0088ff', '#00c8ff', '#0044cc', '#00aaee',
        '#4488ff', '#0066dd', '#00e5ff', '#1155bb'
    ]

    if chart_type == "table":
        st.dataframe(df, use_container_width=True)

    elif chart_type == "bar":
        x = chart_config.get("x", df.columns[0])
        y = chart_config.get("y", df.columns[1])
        color = chart_config.get("color")
        if color and color in df.columns:
            fig = px.bar(df, x=x, y=y, color=color, title=chart_config.get("title"),
                         color_discrete_sequence=blue_palette)
        else:
            fig = px.bar(df, x=x, y=y, title=chart_config.get("title"),
                         color_discrete_sequence=blue_palette)
        fig.update_traces(marker_line_color='rgba(0,160,255,0.3)', marker_line_width=0.5)
        fig.update_layout(**glass_layout, showlegend=True, hovermode='x unified',
                          hoverlabel=dict(bgcolor='rgba(0,30,80,0.85)', bordercolor='rgba(0,140,255,0.4)',
                                         font=dict(color='#c0e0ff')))
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "line":
        x = chart_config.get("x", df.columns[0])
        y = chart_config.get("y", [df.columns[1]])
        fig = px.line(df, x=x, y=y, title=chart_config.get("title"),
                      color_discrete_sequence=blue_palette)
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(**glass_layout, showlegend=True, hovermode='x unified',
                          hoverlabel=dict(bgcolor='rgba(0,30,80,0.85)', bordercolor='rgba(0,140,255,0.4)',
                                         font=dict(color='#c0e0ff')))
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "pie":
        names = chart_config.get("names", df.columns[0])
        values = chart_config.get("values", df.columns[1])
        fig = px.pie(df, names=names, values=values, title=chart_config.get("title"),
                     color_discrete_sequence=blue_palette)
        pie_layout = {k: v for k, v in glass_layout.items() if k not in ['xaxis', 'yaxis']}
        fig.update_traces(textfont=dict(color='white'),
                          marker=dict(line=dict(color='rgba(0,20,60,0.8)', width=2)))
        fig.update_layout(**pie_layout)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "scatter":
        x = chart_config.get("x", df.columns[0])
        y = chart_config.get("y", df.columns[1])
        color = chart_config.get("color")
        size = chart_config.get("size")
        if color and size:
            fig = px.scatter(df, x=x, y=y, color=color, size=size,
                             title=chart_config.get("title"), color_discrete_sequence=blue_palette)
        elif color:
            fig = px.scatter(df, x=x, y=y, color=color,
                             title=chart_config.get("title"), color_discrete_sequence=blue_palette)
        else:
            fig = px.scatter(df, x=x, y=y, title=chart_config.get("title"),
                             color_discrete_sequence=blue_palette)
        fig.update_layout(**glass_layout)
        st.plotly_chart(fig, use_container_width=True)

    else:
        fig = px.bar(df, title=chart_config.get("title"), color_discrete_sequence=blue_palette)
        fig.update_layout(**glass_layout)
        st.plotly_chart(fig, use_container_width=True)


# Fetch table info on load
if st.session_state.table_info is None:
    fetch_table_info()

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    <div style="display:inline-block; background: rgba(0,80,200,0.15); border:1px solid rgba(0,140,255,0.25);
                border-radius: 30px; padding: 4px 16px; margin-bottom: 1rem;">
        <span class="badge">✦ AI-POWERED ANALYTICS</span>
    </div>
    <h1 class="main-header">📊 Conversational BI Dashboard</h1>
    <p class="sub-header">Ask questions in plain English — get instant, intelligent visualizations</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.2rem 0 0.6rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.4rem;">
            <div style="width:28px;height:28px;border-radius:8px;
                        background:linear-gradient(135deg,#1a7fff,#0044cc);
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.85rem;box-shadow:0 2px 10px rgba(0,100,255,0.4);
                        flex-shrink:0;">🤖</div>
            <span style="font-family:'Syne',sans-serif;font-size:0.88rem;font-weight:700;
                         background:linear-gradient(120deg,#a8d8ff,#3ab0ff);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                Gemini BI Engine
            </span>
        </div>
        <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,140,255,0.35),transparent);margin-bottom:0.5rem;"></div>
        <p style="font-size:0.65rem;color:rgba(120,180,255,0.55);margin:0;letter-spacing:0.4px;">
            Natural language → SQL → Visualization
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section-title">💡 Try asking</p>', unsafe_allow_html=True)

    example_queries = [
        ("📊", "Total claims by status"),
        ("📍", "Avg claim amount by state"),
        ("📈", "Claim trends over time"),
        ("🏆", "Top 10 highest claims"),
    ]
    for icon, text in example_queries:
        st.markdown(f"""
        <div class="sidebar-item">
            <span class="icon">{icon}</span>
            <span class="text">{text}</span>
        </div>""", unsafe_allow_html=True)

    st.divider()

    st.markdown('<p class="sidebar-section-title">📁 Dataset</p>', unsafe_allow_html=True)
    uploaded_file_sidebar = st.file_uploader("Upload CSV", type="csv", label_visibility="collapsed")
    if uploaded_file_sidebar is not None:
        if st.button("⬆️ Upload & Use", use_container_width=True):
            if upload_file(uploaded_file_sidebar):
                st.rerun()

    st.divider()

    if st.button("🔄 Refresh Schema", use_container_width=True):
        fetch_table_info()

    if st.session_state.table_info:
        cols = st.session_state.table_info.get('columns', [])
        with st.expander(f"📋 Schema  ·  {len(cols)} cols"):
            for col in cols[:10]:
                st.markdown(f"<span class='badge'>{col}</span>&nbsp;", unsafe_allow_html=True)
            if len(cols) > 10:
                st.markdown(f"<span style='font-size:0.65rem;color:rgba(100,160,255,0.5)'>+{len(cols)-10} more</span>", unsafe_allow_html=True)

# ── Query Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="query-section">', unsafe_allow_html=True)
col_main, col_btn = st.columns([3, 1])

with col_main:
    query_input_text = st.text_input(
        "💬 Ask a question about your data:",
        placeholder="e.g., Show me total claims paid by state as a bar chart...",
        key="query_input_text"
    )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    submit_btn = st.button("🚀 Generate", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Clarifying Questions ──────────────────────────────────────────────────────
if st.session_state.clarifying_questions:
    st.markdown("""
    <div style="background:rgba(0,80,160,0.2); border:1px solid rgba(0,160,255,0.3);
                border-radius:12px; padding:1rem 1.2rem; margin:1rem 0;">
        <span style="color:#60c8ff; font-weight:600;">🤔 Clarification needed</span>
    </div>
    """, unsafe_allow_html=True)
    for i, question in enumerate(st.session_state.clarifying_questions):
        st.write(f"**{i+1}.** {question}")

    clarification_text = st.text_input("Your clarification:", key="clarification_input_text")
    if clarification_text and st.button("Submit Clarification"):
        enhanced_q = f"{st.session_state.last_query} ({clarification_text})"
        res = process_query_func(enhanced_q)
        if res:
            st.session_state.current_data = res["data"]
            st.session_state.current_chart = res["chart_config"]
            st.session_state.sql_query = res["sql_query"]
            st.session_state.chat_history.append({
                "query": enhanced_q,
                "timestamp": datetime.now(),
                "row_count": res["row_count"],
                "execution_time": res["execution_time"]
            })
            st.session_state.clarifying_questions = None
            st.rerun()

# ── Process Query ─────────────────────────────────────────────────────────────
if submit_btn and query_input_text:
    q_questions = get_clarifying_questions(query_input_text)
    if q_questions and len(q_questions) > 0:
        st.session_state.clarifying_questions = q_questions
        st.session_state.last_query = query_input_text
        st.rerun()
    else:
        res = process_query_func(query_input_text)
        if res:
            st.session_state.current_data = res["data"]
            st.session_state.current_chart = res["chart_config"]
            st.session_state.sql_query = res["sql_query"]
            st.session_state.current_reasoning = res.get("ai_reasoning")
            st.session_state.current_suggestions = res.get("suggestions", [])
            st.session_state.chat_history.append({
                "query": query_input_text,
                "timestamp": datetime.now(),
                "row_count": res["row_count"],
                "execution_time": res["execution_time"]
            })
            st.session_state.clarifying_questions = None

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.current_data is not None:

    if st.session_state.sql_query == "INSUFFICIENT_DATA":
        st.error("❌ **This question cannot be answered with the available data.**\n\n"
                 "The dataset does not contain the information you requested.")
        suggestions = st.session_state.current_suggestions
        if suggestions:
            st.markdown("### 💡 Try instead:")
            for s in suggestions:
                st.markdown(f"- {s}")
        reasoning = st.session_state.current_reasoning or {}
        with st.expander("🧠 AI Reasoning"):
            missing = reasoning.get("missing_fields")
            if missing:
                st.markdown(f"**Missing fields:** `{', '.join(missing)}`")
            if "error" in reasoning:
                st.caption(f"Error: {reasoning['error']}")
    else:
        # Metrics
        st.markdown("<br>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        df_current = pd.DataFrame(st.session_state.current_data)

        with m_col1:
            st.metric("📊 Rows Returned", len(df_current))
        with m_col2:
            num_cols = df_current.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                total_val = df_current[num_cols[0]].sum()
                st.metric("💰 Primary Sum", f"{total_val:,.0f}")
        with m_col3:
            if st.session_state.chat_history:
                last_item = st.session_state.chat_history[-1]
                st.metric("⚡ Response Time", f"{last_item['execution_time']:.2f}s")
        with m_col4:
            if st.session_state.sql_query:
                with st.expander("🔍 SQL Query"):
                    st.code(st.session_state.sql_query, language="sql")

        # AI Reasoning
        if st.session_state.current_reasoning:
            reasoning = st.session_state.current_reasoning
            st.markdown("---")
            st.markdown("### 🧠 AI Reasoning")
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                if reasoning.get("fast_path"):
                    st.success("⚡ Fast Path: SQL Template Matched")
                    st.write(f"**Detected Intent:** `{reasoning.get('intent', 'Unknown')}`")
                else:
                    st.info("🤖 Full LLM Reasoning Applied")
                    st.write(f"**Columns Used:** `{reasoning.get('relevant_columns', 'Unknown')}`")
            with r_col2:
                if reasoning.get("fast_path"):
                    st.write("**Extracted Parameters:**")
                    st.json(reasoning.get("extracted_parameters", {}))
                else:
                    answerable = '✅ YES' if reasoning.get('is_answerable') else '❌ NO'
                    st.write(f"**Answerable:** {answerable}")

        # Chart
        st.markdown("---")
        st.subheader("📈 Visualization")
        str_chart = st.session_state.current_chart
        if str_chart and (str_chart.get("type") != "table" or len(df_current) > 0):
            render_chart(str_chart)

        # Raw data
        if len(df_current) > 0:
            with st.expander("📋 View Raw Data"):
                st.dataframe(df_current, use_container_width=True)
                csv_data = df_current.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# ── Chat History ──────────────────────────────────────────────────────────────
if st.session_state.chat_history:
    st.divider()
    st.subheader("📝 Recent Queries")

    for i, chat_item in enumerate(reversed(st.session_state.chat_history[-5:])):
        h_col1, h_col2 = st.columns([6, 1])
        with h_col1:
            st.info(f"**Q:** {chat_item['query']}\n\n"
                    f"🕒 {chat_item['timestamp'].strftime('%H:%M:%S')}  ·  "
                    f"📊 {chat_item['row_count']} rows  ·  "
                    f"⚡ {chat_item['execution_time']:.2f}s")
        with h_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄", key=f"re_run_{i}"):
                res_rerun = process_query_func(chat_item['query'])
                if res_rerun:
                    st.session_state.current_data = res_rerun["data"]
                    st.session_state.current_chart = res_rerun["chart_config"]
                    st.session_state.sql_query = res_rerun["sql_query"]
                    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; padding:0.5rem 0;">
    <span style="color:rgba(80,140,220,0.5); font-size:0.78rem; letter-spacing:0.5px;">
        <span class="pulse-dot"></span>
        Powered by Google Gemini AI  ·  FastAPI + Streamlit  ·  Glassmorphism UI
    </span>
</div>
""", unsafe_allow_html=True)
