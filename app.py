import streamlit as st
import requests
import json


st.set_page_config(
    page_title  = "CodeIS — IS 875 Intelligence",
    page_icon   = "🏗️",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

API_URL = "http://localhost:8000"


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Force light color-scheme so browsers don't auto-dark-mode
   native form controls (textarea/input/select). This is the root
   cause of "white text on white background" — without this, some
   browsers apply forced-dark styling to native widgets regardless
   of the background color you set in CSS. ── */
:root {
    color-scheme: light;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color-scheme: light;
}

/* ── Hide default Streamlit elements ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* ── Main background ── */
.stApp {
    background: #F7F8FC;
}

/* ── Hero Header ── */
.hero-section {
    background: linear-gradient(135deg, #0F2D5E 0%, #1A4A8A 60%, #2563B0 100%);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -30%;
    right: 10%;
    width: 250px;
    height: 250px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.75);
    margin-top: 0.4rem;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #fff;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 1rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.hero-stats {
    display: flex;
    gap: 2rem;
    margin-top: 1.5rem;
}
.hero-stat {
    text-align: left;
}
.hero-stat-number {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}
.hero-stat-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.6);
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Query box: this targets the real st.container(border=True) wrapper
   used around the "Ask anything about IS 875" section ── */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.query-label) {
    background: #FFFFFF;
    border-radius: 12px !important;
    border: 1px solid #F1F5F9 !important;
    padding: 0.5rem 0.5rem 1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 1.2rem;
}
.query-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
    margin: 0.6rem 0 0.6rem 0.2rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Answer card ── */
.answer-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
    border-left: 4px solid #1A4A8A;
    margin-bottom: 1.2rem;
}
.answer-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #1A4A8A;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}
.answer-text {
    font-size: 1rem;
    color: #1F2937;
    line-height: 1.75;
}

/* ── Clause pills ── */
.clause-pill {
    display: inline-block;
    background: #EEF2FF;
    color: #1A4A8A;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 3px 4px 3px 0;
    border: 1px solid #C7D2FE;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.2rem;
}
.metric-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(15,45,94,0.10);
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0F2D5E;
    line-height: 1;
}
.metric-label {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    font-weight: 500;
}

/* ── Confidence bar ── */
.conf-bar-bg {
    background: #E5E7EB;
    border-radius: 4px;
    height: 6px;
    margin-top: 8px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #1A4A8A, #2563B0);
}

/* ── Source card ── */
.source-item {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.source-badge {
    background: #0F2D5E;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
}
.source-score {
    font-size: 0.8rem;
    font-weight: 600;
    color: #1A4A8A;
}
.source-meta {
    font-size: 0.8rem;
    color: #6B7280;
    margin-bottom: 0.4rem;
}
.source-snippet {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #374151;
    background: #F3F4F6;
    padding: 0.6rem 0.8rem;
    border-radius: 6px;
    overflow-x: auto;
    white-space: nowrap;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0F2D5E !important;
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* The selectbox itself renders a white internal box (BaseWeb component) —
   the blanket white-text rule above makes its text invisible against that
   white background. Override color back to dark specifically inside it. */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #1F2937 !important;
    -webkit-text-fill-color: #1F2937 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] input {
    caret-color: #1F2937 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: #1F2937 !important;
}
/* Disabled state (when Multi-Hop Retrieval is on) should look visibly
   disabled rather than just empty */
section[data-testid="stSidebar"] div[data-baseweb="select"][aria-disabled="true"] {
    background-color: #E5E7EB !important;
    opacity: 0.7;
}
/* The dropdown options popover — keep it light and legible too */
div[data-baseweb="popover"] li {
    color: #1F2937 !important;
}
.sidebar-logo {
    font-size: 1.4rem;
    font-weight: 700;
    color: white !important;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.sidebar-tagline {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.5) !important;
    margin-bottom: 1.5rem;
}
.status-ready {
    background: rgba(16,185,129,0.2);
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-size: 0.82rem;
    color: #6EE7B7 !important;
    font-weight: 600;
}
.status-error {
    background: rgba(239,68,68,0.2);
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-size: 0.82rem;
    color: #FCA5A5 !important;
}

/* ── Divider ── */
.section-divider {
    height: 1px;
    background: #E5E7EB;
    margin: 1.5rem 0;
}

/* ── Section title ── */
.section-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.75rem;
}

/* ── Streamlit overrides ── */

/* Main-area text area — THIS is the fix for the white-on-white bug.
   We explicitly set color + caret-color so the typed text and cursor
   are always visible regardless of the user's OS/browser dark mode. */
.stTextArea textarea {
    border-radius: 8px !important;
    border: 1.5px solid #E5E7EB !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    background-color: #FAFAFA !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    transition: border 0.2s !important;
}
.stTextArea textarea::placeholder {
    color: #9CA3AF !important;
    opacity: 1 !important;
}
.stTextArea textarea:focus {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    border-color: #1A4A8A !important;
    box-shadow: 0 0 0 3px rgba(26,74,138,0.1) !important;
}

.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton button[kind="primary"] {
    background: #0F2D5E !important;
    border: none !important;
    padding: 0.6rem 1.5rem !important;
    color: #FFFFFF !important;
}
.stButton button[kind="primary"]:hover {
    background: #1A4A8A !important;
}
.stButton button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #1A4A8A !important;
    border: 1.5px solid #E2E8F0 !important;
    box-shadow: 0 1px 2px rgba(15,45,94,0.04) !important;
    transition: all 0.15s ease !important;
}
.stButton button[kind="secondary"]:hover {
    background-color: #F0F4FF !important;
    border-color: #1A4A8A !important;
    color: #0F2D5E !important;
    box-shadow: 0 4px 12px rgba(15,45,94,0.12) !important;
    transform: translateY(-1px);
}
.stButton button[kind="secondary"]:active {
    transform: translateY(0);
}
/* Example-question buttons specifically: left-aligned text reads better
   than centered for a "question chip" */
div[data-testid="stExpander"] .stButton button p {
    text-align: left !important;
    white-space: normal !important;
}

/* ── Expanders (Try Example Questions, Source Verification cards) ── */
div[data-testid="stExpander"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    background: #FFFFFF !important;
    color: #0F2D5E !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.9rem 1.2rem !important;
}
div[data-testid="stExpander"] summary:hover {
    background: #F8FAFC !important;
}
div[data-testid="stExpander"] summary svg {
    fill: #1A4A8A !important;
}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background: #FFFFFF !important;
    padding: 1.1rem 1.2rem 1.3rem !important;
    border-top: 1px solid #F1F5F9;
}

/* ── Alerts (st.info / st.success / st.warning / st.error) ── */
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}

/* ── Sidebar form controls — tint to match brand navy ── */
section[data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {
    background-color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏗️ CodeIS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">IS 875 Intelligence Platform</div>', unsafe_allow_html=True)

    # DB Status
    try:
        r = requests.get(f"{API_URL}/status", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data["status"] == "ready":
                st.markdown(f'<div class="status-ready">✅ Ready — {data["chunk_count"]} clauses indexed<br><span style="font-weight:400;font-size:0.75rem;opacity:0.8">LLM: {data["llm_provider"].upper()}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-error">❌ DB Empty — run ingestion</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">⚠️ API not responding</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="status-error">❌ API offline<br><span style="font-size:0.75rem;font-weight:400">Run: python api.py</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**⚙️ QUERY SETTINGS**")

    multi_hop = st.toggle("Multi-Hop Retrieval", value=False,
        help="Search across all IS 875 parts simultaneously")

    filter_part = st.selectbox("Filter by Part", options=[
        "All Parts",
        "IS 875 Part 1 - Dead Loads",
        "IS 875 Part 2 - Imposed Loads",
        "IS 875 Part 3 - Wind Loads",
    ], disabled=multi_hop)
    if filter_part == "All Parts":
        filter_part = None

    top_k = st.slider("Chunks to Retrieve", 2, 10, 5)

    st.markdown("---")
    st.markdown("**📚 COVERAGE**")
    st.markdown("""
    <div style="font-size:0.8rem; line-height:1.8; color:rgba(255,255,255,0.7) !important;">
    • IS 875 Part 1 — Dead Loads<br>
    • IS 875 Part 2 — Imposed Loads<br>
    • IS 875 Part 3 — Wind Loads
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:rgba(255,255,255,0.4) !important; line-height:1.8;">
    IITISoC 2026 · CiviLogic · PS2<br>
    RAG · ChromaDB · Gemini AI
    </div>
    """, unsafe_allow_html=True)


#  Hero Section 
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">IITISoC 2026 · CiviLogic · PS2</div>
    <div class="hero-title">CodeIS</div>
    <div class="hero-subtitle">Intelligent Query System for Indian Standard Codes · Powered by RAG + Gemini AI</div>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-number">332</div>
            <div class="hero-stat-label">Clauses Indexed</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-number">3</div>
            <div class="hero-stat-label">IS 875 Parts</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-number">RAG</div>
            <div class="hero-stat-label">Architecture</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-number">BM25+</div>
            <div class="hero-stat-label">Hybrid Retrieval</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Example Questions 
with st.expander("💡 Try Example Questions", expanded=False):
    examples = [
        "What is the design wind speed formula as per IS 875 Part 3?",
        "What is the imposed floor load for residential bedrooms?",
        "What is the unit weight of reinforced cement concrete?",
        "What is the basic wind speed for Chennai?",
        "What is the internal pressure coefficient for medium permeability buildings?",
        "What is the wind pressure formula at height z?",
        "What is the unit weight of steel as per IS 875 Part 1?",
        "What is the imposed load for hospital wards?",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, use_container_width=True, key=f"ex_{i}"):
            st.session_state["prefilled_query"] = ex
            st.session_state["auto_submit"] = True


#  Query Input 
with st.container(border=True):
    st.markdown('<div class="query-label">Ask anything about IS 875</div>', unsafe_allow_html=True)

    prefilled = st.session_state.pop("prefilled_query", "")
    query = st.text_area(
        label     = "query_input",
        value     = prefilled,
        height    = 90,
        placeholder = "e.g. What is the design wind pressure formula as per IS 875 Part 3?",
        label_visibility = "collapsed",
    )

    col_btn, col_clear, col_info = st.columns([1.2, 1, 5])
    submit = col_btn.button("🔍  Search", type="primary", use_container_width=True)
    if col_clear.button("✕ Clear", use_container_width=True):
        st.session_state.pop("last_response", None)
        st.rerun()

    if st.session_state.pop("auto_submit", False):
        submit = True


# Process Query 
if submit and query.strip():
    with st.spinner("Retrieving relevant clauses and generating answer..."):
        try:
            payload = {
                "question":    query,
                "top_k":       top_k,
                "multi_hop":   multi_hop,
                "filter_part": filter_part,
            }
            r = requests.post(f"{API_URL}/query", json=payload, timeout=120)
            r.raise_for_status()
            response = r.json()
            st.session_state["last_response"] = response
            # Add to history
            if "history" not in st.session_state:
                st.session_state["history"] = []
            st.session_state["history"].insert(0, {
                "q": query,
                "a": response["answer"][:120] + "...",
                "conf": response.get("confidence", 0),
            })
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure `python api.py` is running.")
        except Exception as e:
            st.error(f"❌ Error: {e}")


if "last_response" in st.session_state:
    resp = st.session_state["last_response"]
    conf = resp.get("confidence", 0)
    latency = resp.get("latency_s", 0)
    sources = resp.get("sources", [])

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-value">{conf:.0%}</div>
            <div class="metric-label">Confidence</div>
            <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{min(conf*100,100):.0f}%"></div></div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{latency:.1f}s</div>
            <div class="metric-label">Latency</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(sources)}</div>
            <div class="metric-label">Sources Used</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Answer
    st.markdown(f"""
    <div class="answer-card">
        <div class="answer-title">📋 Answer</div>
        <div class="answer-text">{resp["answer"].replace(chr(10), "<br>")}</div>
    </div>
    """, unsafe_allow_html=True)

    if resp.get("cited_clauses"):
        pills = "".join(f'<span class="clause-pill">{c}</span>' for c in resp["cited_clauses"])
        st.markdown(f'<div style="margin-bottom:1rem"><div class="section-title">Referenced Clauses</div>{pills}</div>', unsafe_allow_html=True)

    if resp.get("is_multi_hop"):
        st.info("🔀 Multi-hop query — retrieved from all IS 875 parts")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗂️ Source Verification</div>', unsafe_allow_html=True)

    for i, src in enumerate(sources, 1):
        score = src.get("fused_score", 0)
        clause = src.get("clause_number", "N/A")
        part = src.get("part_name", "IS 875")
        pages = src.get("page_numbers", "N/A")
        snippet = src.get("text_snippet", "")[:150]

        with st.expander(f"[{i}] {part} — Clause {clause}  ·  Score: {score:.2f}", expanded=(i==1)):
            st.markdown(f"""
            <div class="source-item">
                <div class="source-header">
                    <span class="source-badge">CLAUSE {clause}</span>
                    <span class="source-score">Relevance {score:.2f}</span>
                </div>
                <div class="source-meta">{part} &nbsp;·&nbsp; Pages {pages}</div>
                <div class="source-snippet">{snippet}</div>
            </div>
            """, unsafe_allow_html=True)

    # Feedback
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Was this answer helpful?</div>', unsafe_allow_html=True)
    fb1, fb2, _ = st.columns([1, 1, 6])
    if fb1.button("👍 Yes", key="fb_yes"):
        try:
            requests.post(f"{API_URL}/feedback", json={"question": resp["query"], "answer": resp["answer"], "helpful": True}, timeout=5)
        except: pass
        st.success("Thanks for your feedback!")
    if fb2.button("👎 No", key="fb_no"):
        try:
            requests.post(f"{API_URL}/feedback", json={"question": resp["query"], "answer": resp["answer"], "helpful": False}, timeout=5)
        except: pass
        st.warning("Feedback recorded. We'll improve!")


#  Session History in Sidebar 
with st.sidebar:
    if st.session_state.get("history"):
        st.markdown("---")
        st.markdown("**🕑 RECENT QUERIES**")
        for item in st.session_state["history"][:4]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.07);border-radius:6px;padding:0.5rem 0.7rem;margin-bottom:0.4rem;font-size:0.75rem;">
                <div style="color:rgba(255,255,255,0.9)!important;font-weight:500;margin-bottom:2px;">{item['q'][:55]}...</div>
                <div style="color:rgba(255,255,255,0.45)!important;">Confidence: {item['conf']:.0%}</div>
            </div>
            """, unsafe_allow_html=True)