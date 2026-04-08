import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Conversational BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ─ Page background */
.stApp { background: #0a0d14; }

/* ─ Sidebar */
[data-testid="stSidebar"] {
    background: #0f1117 !important;
    border-right: 1px solid #1a1f2e;
}
[data-testid="stSidebar"] > div:first-child { padding: 1.25rem 1rem 2rem; }

.sb-logo {
    display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;
    padding-bottom: 1.25rem; border-bottom: 1px solid #1a1f2e;
}
.sb-logo-icon { font-size: 2rem; }
.sb-logo-title {
    font-family: 'Space Mono', monospace; font-size: 0.8rem; font-weight: 700;
    color: #e2e8f0; letter-spacing: 0.08em; text-transform: uppercase; line-height: 1.3;
}
.sb-logo-sub { font-size: 0.65rem; color: #4a5568; margin-top: 2px; }

.sb-label {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: #4a5568;
    margin: 1.25rem 0 0.5rem; padding-bottom: 0.3rem; border-bottom: 1px solid #1a1f2e;
}

.sb-pill {
    display: flex; align-items: center; gap: 8px;
    background: #131720; border: 1px solid #1a1f2e;
    border-radius: 8px; padding: 0.5rem 0.75rem; margin-bottom: 0.4rem;
}
.sb-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.sb-dot.g { background: #38a169; box-shadow: 0 0 5px #38a16990; }
.sb-dot.r { background: #e53e3e; box-shadow: 0 0 5px #e53e3e90; }
.sb-dot.y { background: #d69e2e; box-shadow: 0 0 5px #d69e2e90; }
.sb-pill-text { font-size: 0.7rem; color: #a0aec0; }

.sb-schema {
    background: #131720; border: 1px solid #1a1f2e; border-radius: 10px;
    padding: 0.7rem 0.85rem; font-size: 0.7rem; color: #718096; line-height: 1.75;
    margin-bottom: 0.5rem;
}
.sb-schema .k { color: #4a5568; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.08em; }
.sb-schema .v { color: #90cdf4; font-weight: 500; }

.sb-footer {
    margin-top: 2rem; padding-top: 0.85rem; border-top: 1px solid #1a1f2e;
    font-size: 0.6rem; color: #2d3748; text-align: center; letter-spacing: 0.04em;
}

/* ─ Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: #131720 !important; border: 1px solid #1a1f2e !important;
    color: #718096 !important; border-radius: 8px !important;
    font-size: 0.73rem !important; width: 100%; text-align: left !important;
    padding: 0.45rem 0.85rem !important;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a2035 !important; border-color: #4361ee !important; color: #c3cfe2 !important;
}

/* ─ Hero header */
.hero {
    text-align: center; padding: 2rem 0 1.5rem;
}
.hero-title {
    font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700;
    color: #e2e8f0; letter-spacing: -0.01em; margin-bottom: 0.35rem;
}
.hero-sub { font-size: 0.95rem; color: #4a5568; }

/* ─ Query bar */
.query-wrap {
    background: #0f1117; border: 1px solid #1a1f2e; border-radius: 14px;
    padding: 1.25rem 1.5rem; margin-bottom: 1.25rem;
}

/* ─ Metric cards */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.25rem; }
.metric-card {
    flex: 1; background: #0f1117; border: 1px solid #1a1f2e; border-radius: 12px;
    padding: 1rem 1.25rem;
}
.metric-label { font-size: 0.65rem; color: #4a5568; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.5rem; color: #90cdf4; font-weight: 700; }
.metric-sub { font-size: 0.65rem; color: #4a5568; margin-top: 2px; }

/* ─ Section card */
.section-card {
    background: #0f1117; border: 1px solid #1a1f2e; border-radius: 14px;
    padding: 1.25rem 1.5rem; margin-bottom: 1rem;
}
.section-title {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #4a5568; margin-bottom: 1rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid #1a1f2e;
}

/* ─ History item */
.hist-item {
    background: #131720; border: 1px solid #1a1f2e; border-radius: 8px;
    padding: 0.65rem 0.9rem; margin-bottom: 0.5rem;
}
.hist-q { font-size: 0.8rem; color: #a0aec0; margin-bottom: 3px; }
.hist-meta { font-size: 0.65rem; color: #4a5568; }

/* ─ Plotly dark overrides */
.stPlotlyChart { background: transparent !important; }

/* ─ Streamlit widget tweaks */
[data-testid="stTextInput"] > div > div > input {
    background: #131720 !important; border: 1px solid #2d3748 !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
    font-size: 0.9rem !important;
}
[data-testid="stMetricValue"] { color: #90cdf4 !important; }
div[data-testid="stDataFrame"] { background: #0f1117 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "chat_history": [],
    "current_data": None,
    "current_chart": None,
    "sql_query": None,
    "table_info": None,
    "clarifying_questions": None,
    "last_query": "",
    "pending_query": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── API helpers ───────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=10)
        return r.json() if r.ok else None
    except Exception:
        return None

def api_post(path, payload):
    try:
        r = requests.post(f"{API_URL}{path}", json=payload, timeout=60)
        return r.json() if r.ok else {"error": r.text}
    except Exception as e:
        return {"error": str(e)}

def fetch_table_info():
    info = api_get("/table-info")
    if info and "error" not in info:
        st.session_state.table_info = info

def run_and_store(query: str):
    with st.spinner("🧠 Generating SQL and fetching results…"):
        res = api_post("/query", {"query": query})
    if "error" in res:
        st.error(f"❌ {res['error']}")
        return
    st.session_state.current_data   = res["data"]
    st.session_state.current_chart  = res["chart_config"]
    st.session_state.sql_query      = res["sql_query"]
    st.session_state.clarifying_questions = None
    st.session_state.chat_history.append({
        "query":          query,
        "timestamp":      datetime.now(),
        "row_count":      res["row_count"],
        "execution_time": res["execution_time"],
        "sql":            res["sql_query"],
    })

def render_chart(cfg):
    if not cfg or not cfg.get("data"):
        st.info("No data returned.")
        return
    df = pd.DataFrame(cfg["data"])
    t  = cfg.get("type", "table")
    title = cfg.get("title", "")

    LAYOUT = dict(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font_color="#a0aec0", title_font_color="#e2e8f0",
        title_font_size=14, margin=dict(l=20, r=20, t=45, b=20),
        xaxis=dict(gridcolor="#1a1f2e", linecolor="#1a1f2e"),
        yaxis=dict(gridcolor="#1a1f2e", linecolor="#1a1f2e"),
    )
    COLOR_SEQ = px.colors.qualitative.Plotly

    if t == "bar":
        x, y = cfg.get("x", df.columns[0]), cfg.get("y", df.columns[1])
        c = cfg.get("color")
        fig = px.bar(df, x=x, y=y, color=c if c and c in df.columns else None,
                     title=title, color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(**LAYOUT, showlegend=bool(c), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    elif t == "line":
        x  = cfg.get("x", df.columns[0])
        ys = cfg.get("y", df.columns[1])
        if isinstance(ys, str):
            ys = [ys]
        fig = px.line(df, x=x, y=ys, title=title, markers=True,
                      color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(**LAYOUT, showlegend=True, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    elif t == "pie":
        fig = px.pie(df, names=cfg.get("names", df.columns[0]),
                     values=cfg.get("values", df.columns[1]), title=title,
                     color_discrete_sequence=COLOR_SEQ, hole=0.35)
        fig.update_layout(**{k: v for k, v in LAYOUT.items()
                             if k not in ("xaxis", "yaxis")})
        st.plotly_chart(fig, use_container_width=True)

    elif t == "scatter":
        fig = px.scatter(df, x=cfg.get("x", df.columns[0]),
                         y=cfg.get("y", df.columns[1]),
                         color=cfg.get("color"), size=cfg.get("size"),
                         title=title, color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    else:  # table
        st.dataframe(df, use_container_width=True, height=380)

# ── First load ────────────────────────────────────────────────────────────────
if st.session_state.table_info is None:
    fetch_table_info()

backend_ok = st.session_state.table_info is not None

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
EXAMPLES = [
    ("📋", "Show total claim amount by insurer"),
    ("📍", "Average claim amount by state"),
    ("📈", "Trend of claims over year"),
    ("🔄", "Claim status breakdown by policy type"),
    ("💰", "Top 10 states by total claim amount"),
    ("⏱️",  "Average settlement days by insurer"),
    ("👥", "Claims count by gender and status"),
    ("📅", "Monthly claim count trend for 2022"),
]

with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <span class="sb-logo-icon">📊</span>
        <div>
            <div class="sb-logo-title">BI Dashboard</div>
            <div class="sb-logo-sub">Conversational Analytics · Gemini AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    st.markdown('<div class="sb-label">System Status</div>', unsafe_allow_html=True)
    d1, l1 = ("g", "Backend · Connected") if backend_ok else ("r", "Backend · Offline")
    st.markdown(f'<div class="sb-pill"><span class="sb-dot {d1}"></span>'
                f'<span class="sb-pill-text">{l1}</span></div>', unsafe_allow_html=True)

    if backend_ok and st.session_state.table_info:
        cols = st.session_state.table_info.get("columns", [])
        d2, l2 = "g", f"Dataset · {st.session_state.table_info.get('row_count', '?'):,} rows"
    else:
        d2, l2 = "y", "Dataset · Not loaded"
    st.markdown(f'<div class="sb-pill"><span class="sb-dot {d2}"></span>'
                f'<span class="sb-pill-text">{l2}</span></div>', unsafe_allow_html=True)

    # Schema info
    if backend_ok and st.session_state.table_info:
        info = st.session_state.table_info
        cols = info.get("columns", [])
        st.markdown('<div class="sb-label">Dataset Schema</div>', unsafe_allow_html=True)
        preview = " · ".join(cols[:5]) + (f" +{len(cols)-5} more" if len(cols) > 5 else "")
        st.markdown(f"""
        <div class="sb-schema">
            <div><span class="k">Table</span><br><span class="v">claims</span></div>
            <div style="margin-top:0.5rem"><span class="k">Columns ({len(cols)})</span><br><span class="v" style="font-size:0.65rem">{preview}</span></div>
            <div style="margin-top:0.5rem"><span class="k">Rows</span><br><span class="v">{info.get('row_count', 0):,}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄  Refresh Schema", key="refresh"):
            fetch_table_info()
            st.rerun()

    # Upload
    st.markdown('<div class="sb-label">Upload Dataset</div>', unsafe_allow_html=True)
    up = st.file_uploader("CSV file", type="csv", label_visibility="collapsed")
    if up:
        if st.button("⬆  Upload & Use Dataset", key="upload_btn"):
            with st.spinner("Uploading…"):
                try:
                    r = requests.post(f"{API_URL}/upload",
                                      files={"file": (up.name, up, "text/csv")}, timeout=30)
                    if r.ok:
                        st.success("✅ Dataset loaded!")
                        fetch_table_info()
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {r.text}")
                except Exception as e:
                    st.error(str(e))

    # Example chips
    st.markdown('<div class="sb-label">Example Queries</div>', unsafe_allow_html=True)
    for icon, text in EXAMPLES:
        if st.button(f"{icon}  {text}", key=f"ex_{text[:20]}", use_container_width=True):
            st.session_state.pending_query = text

    st.markdown('<div class="sb-footer">FastAPI · SQLite · Gemini · Streamlit · Plotly</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-title">📊 Conversational BI Dashboard</div>
    <div class="hero-sub">Ask questions in plain English — get instant SQL, charts, and insights</div>
</div>
""", unsafe_allow_html=True)

# Grab pending chip query before rendering the input
pending = st.session_state.pending_query
if pending:
    st.session_state.pending_query = ""

# ── Query input bar ───────────────────────────────────────────────────────────
st.markdown('<div class="query-wrap">', unsafe_allow_html=True)
col_q, col_btn = st.columns([5, 1])
with col_q:
    query_text = st.text_input(
        "question",
        value=pending,
        placeholder="e.g.  Show me total claim amount by state for 2022",
        label_visibility="collapsed",
        key="query_input",
    )
with col_btn:
    go = st.button("🚀  Run", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Auto-fire from chip
if pending:
    run_and_store(pending)

# Clarifying questions
if st.session_state.clarifying_questions:
    st.info("🤔 Could you clarify?")
    for i, q in enumerate(st.session_state.clarifying_questions):
        st.write(f"{i+1}. {q}")
    clarification = st.text_input("Your clarification:", key="clarify_input")
    if clarification and st.button("Submit"):
        combined = f"{st.session_state.last_query} ({clarification})"
        run_and_store(combined)
        st.rerun()

# Manual submit
if go and query_text and not pending:
    # Check for clarification needs first
    with st.spinner("Checking query…"):
        qs_res = api_post("/clarify", {"query": query_text})
    qs = qs_res.get("questions", []) if isinstance(qs_res, dict) else []
    if qs:
        st.session_state.clarifying_questions = qs
        st.session_state.last_query = query_text
        st.rerun()
    else:
        run_and_store(query_text)

# ── Results area ──────────────────────────────────────────────────────────────
if st.session_state.current_data:
    df = pd.DataFrame(st.session_state.current_data)
    last = st.session_state.chat_history[-1] if st.session_state.chat_history else {}

    # KPI strip
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📊 Rows", f"{len(df):,}")
    with c2:
        if num_cols:
            st.metric("∑ " + num_cols[0], f"{df[num_cols[0]].sum():,.0f}")
    with c3:
        st.metric("⚡ Query time", f"{last.get('execution_time', 0):.3f}s")
    with c4:
        if len(num_cols) > 1:
            st.metric("∅ " + num_cols[1], f"{df[num_cols[1]].mean():,.2f}")
        else:
            st.metric("Columns", len(df.columns))

    # Chart
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Visualization</div>', unsafe_allow_html=True)
    render_chart(st.session_state.current_chart)
    st.markdown('</div>', unsafe_allow_html=True)

    # SQL + raw data
    col_sql, col_data = st.columns([1, 1])
    with col_sql:
        with st.expander("🔍 Generated SQL"):
            st.code(st.session_state.sql_query or "", language="sql")
    with col_data:
        with st.expander("📋 Raw Data"):
            st.dataframe(df, use_container_width=True, height=250)
            st.download_button(
                "📥 Download CSV",
                data=df.to_csv(index=False),
                file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

# ── Query history ─────────────────────────────────────────────────────────────
if st.session_state.chat_history:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Query History</div>', unsafe_allow_html=True)
    for i, item in enumerate(reversed(st.session_state.chat_history[-8:])):
        h1, h2 = st.columns([6, 1])
        with h1:
            ts = item["timestamp"].strftime("%H:%M:%S")
            st.markdown(f"""
            <div class="hist-item">
                <div class="hist-q">💬 {item['query']}</div>
                <div class="hist-meta">🕒 {ts} &nbsp;·&nbsp; 📊 {item['row_count']} rows &nbsp;·&nbsp; ⚡ {item['execution_time']:.3f}s</div>
            </div>
            """, unsafe_allow_html=True)
        with h2:
            if st.button("▶", key=f"rerun_{i}", help="Re-run this query"):
                run_and_store(item["query"])
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;font-size:0.65rem;color:#2d3748;padding:2rem 0 1rem">'
            'Powered by Google Gemini AI · FastAPI · SQLite · Streamlit · Plotly</div>',
            unsafe_allow_html=True)
