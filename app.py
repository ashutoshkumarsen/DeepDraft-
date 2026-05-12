import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeepDraft · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #080810;
    background-image:
        radial-gradient(ellipse 90% 55% at 15% -5%, rgba(255,140,50,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 70% 45% at 85% 110%, rgba(255,70,20,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 50% 60% at 50% 50%, rgba(120,60,255,0.04) 0%, transparent 70%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Noise texture overlay ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 4rem 0 3rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1.2rem;
    opacity: 0.85;
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
}
.hero-eyebrow::before,
.hero-eyebrow::after {
    content: '';
    display: inline-block;
    width: 28px;
    height: 1px;
    background: rgba(255,140,50,0.5);
}
.hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(3.2rem, 7vw, 5.8rem) !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    letter-spacing: -0.045em !important;
    margin: 0 0 1.2rem !important;
}
/* ─── Deep = cream white (was #f8fafc, now warmer cream) ─── */
.hero h1 .deep {
    color: #fdf6ee !important;
    text-shadow: 0 0 60px rgba(253,246,238,0.12);
}
/* Draft = orange */
.hero h1 .draft {
    color: #ff8c32 !important;
    text-shadow: 0 0 80px rgba(255,140,50,0.35);
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #8a8278;
    max-width: 500px;
    margin: 0 auto; /* keep horizontal centering */
    line-height: 1.7;
    text-align: center;

    /* new properties for vertical centering */
    position: relative;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}



/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.25), transparent);
    margin: 2.5rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.12);
    border-radius: 20px;
    padding: 2rem 2.5rem 2.2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.3s;
}
.input-card:hover {
    border-color: rgba(255,140,50,0.22);
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,140,50,0.2) !important;
    border-radius: 12px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1.1rem !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
.stTextInput > div > div > input::placeholder {
    color: #4a4540 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.1), 0 0 20px rgba(255,140,50,0.06) !important;
    background: rgba(255,255,255,0.055) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
    margin-bottom: 0.5rem !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #ff9540 0%, #ff4f10 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.06em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 24px rgba(255,140,50,0.35), 0 1px 0 rgba(255,255,255,0.15) inset !important;
    width: 100%;
    margin-top: 0.8rem !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 36px rgba(255,140,50,0.45) !important;
    opacity: 0.96 !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.99) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s, box-shadow 0.3s;
}
.step-card:hover {
    border-color: rgba(255,255,255,0.1);
}
.step-card.active {
    border-color: rgba(255,140,50,0.45);
    background: rgba(255,140,50,0.05);
    box-shadow: 0 0 32px rgba(255,140,50,0.1), inset 0 0 0 1px rgba(255,140,50,0.1);
}
.step-card.done {
    border-color: rgba(80,200,120,0.3);
    background: rgba(80,200,120,0.03);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 16px 0 0 16px;
    background: rgba(255,255,255,0.04);
    transition: background 0.3s;
}
.step-card.active::before { background: linear-gradient(180deg, #ff9540, #ff5a1a); }
.step-card.done::before   { background: linear-gradient(180deg, #50c878, #2fa855); }

/* ── Animated progress bar inside active card ── */
.step-progress-bar {
    margin-top: 0.9rem;
    height: 2px;
    border-radius: 99px;
    background: rgba(255,255,255,0.05);
    overflow: hidden;
}
.step-progress-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, transparent, #ff8c32, #ffb870, #ff8c32, transparent);
    background-size: 300% 100%;
    animation: shimmer 1.6s linear infinite;
    width: 100%;
}
@keyframes shimmer {
    0%   { background-position: 200% center; }
    100% { background-position: -200% center; }
}

/* ── Pulsing dot ── */
.pulse-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ff8c32;
    margin-right: 5px;
    vertical-align: middle;
    animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.65); }
}

/* ── Done checkmark bounce ── */
.check-icon {
    display: inline-block;
    animation: pop 0.4s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes pop {
    from { transform: scale(0) rotate(-10deg); opacity: 0; }
    to   { transform: scale(1) rotate(0deg); opacity: 1; }
}

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.65;
    min-width: 24px;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #ede8e0;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
}
.status-waiting  { color: #3d3830; }
.status-running  { color: #ff8c32; }
.status-done     { color: #50c878; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.12);
}
.result-content {
    font-size: 0.9rem;
    line-height: 1.85;
    color: #b8b2a8;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,140,50,0.18);
    border-radius: 20px;
    padding: 2.2rem 2.8rem;
    margin-top: 1rem;
    box-shadow: 0 0 60px rgba(255,140,50,0.04);
}
.feedback-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(80,200,120,0.18);
    border-radius: 20px;
    padding: 2.2rem 2.8rem;
    margin-top: 1rem;
    box-shadow: 0 0 60px rgba(80,200,120,0.04);
}
.panel-label {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    text-transform: none;
    margin-bottom: 1.3rem;
    padding-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.panel-label.orange {
    color: #ff8c32;
    border-bottom: 1px solid rgba(255,140,50,0.12);
}
.panel-label.green {
    color: #50c878;
    border-bottom: 1px solid rgba(80,200,120,0.12);
}

/* ── Output section headings ── */
.report-panel h1, .report-panel h2, .report-panel h3, .report-panel h4,
.feedback-panel h1, .feedback-panel h2, .feedback-panel h3, .feedback-panel h4,
.report-panel .stMarkdown h1, .report-panel .stMarkdown h2,
.report-panel .stMarkdown h3, .report-panel .stMarkdown h4,
.feedback-panel .stMarkdown h1, .feedback-panel .stMarkdown h2,
.feedback-panel .stMarkdown h3, .feedback-panel .stMarkdown h4 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    color: #f0ebe0 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.15 !important;
    margin-top: 1.6rem !important;
    margin-bottom: 0.6rem !important;
}
.report-panel h1, .feedback-panel h1,
.report-panel .stMarkdown h1, .feedback-panel .stMarkdown h1 {
    font-size: 2rem !important;
    border-bottom: 1px solid rgba(255,140,50,0.15) !important;
    padding-bottom: 0.4rem !important;
}
.report-panel h2, .feedback-panel h2,
.report-panel .stMarkdown h2, .feedback-panel .stMarkdown h2 {
    font-size: 1.5rem !important;
    color: #f5c896 !important;
}
.report-panel h3, .feedback-panel h3,
.report-panel .stMarkdown h3, .feedback-panel .stMarkdown h3 {
    font-size: 1.2rem !important;
    color: #e0d8cc !important;
}
.report-panel h4, .feedback-panel h4,
.report-panel .stMarkdown h4, .feedback-panel .stMarkdown h4 {
    font-size: 1rem !important;
    color: #c8c0b4 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Spinner ── */
.stSpinner > div { color: #ff8c32 !important; }

/* ── Expander ── */
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    color: #605850 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #ede8e0;
    margin: 1.8rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

/* ── Example chips ── */
.chip-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    align-items: center;
}
.chip-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #3d3830;
    letter-spacing: 0.12em;
}
.chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 0.28rem 0.75rem;
    font-size: 0.75rem;
    color: #8a8278;
    font-family: 'DM Sans', sans-serif;
    cursor: default;
    transition: border-color 0.2s, color 0.2s;
}
.chip:hover {
    border-color: rgba(255,140,50,0.25);
    color: #c8c0b4;
}

/* ── Stats row (hero bottom) ── */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.stat-item {
    text-align: center;
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #ff8c32;
    display: block;
}
.stat-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #4a4540;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* ── Footer ── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #302c28;
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.1em;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}
.notice::before,
.notice::after {
    content: '';
    display: inline-block;
    width: 40px;
    height: 1px;
    background: rgba(255,255,255,0.05);
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    if state == "running":
        status_html = (
            '<span class="step-status status-running">'
            '<span class="pulse-dot"></span>RUNNING'
            '</span>'
        )
        extra_bar = '<div class="step-progress-bar"><div class="step-progress-bar-fill"></div></div>'
        card_cls = "active"
    elif state == "done":
        status_html = (
            '<span class="step-status status-done">'
            '<span class="check-icon">✓</span> DONE'
            '</span>'
        )
        extra_bar = ""
        card_cls = "done"
    else:
        status_html = '<span class="step-status status-waiting">WAITING</span>'
        extra_bar = ""
        card_cls = ""

    desc_html = (
        f"<div style='font-size:0.8rem;color:#3d3830;margin-top:0.25rem;font-family:\"DM Sans\",sans-serif;'>{desc}</div>"
        if desc else ""
    )

    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            {status_html}
        </div>
        {desc_html}
        {extra_bar}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done", "current_step"):
    if key not in st.session_state:
        if key == "results":
            st.session_state[key] = {}
        elif key == "current_step":
            st.session_state[key] = None
        else:
            st.session_state[key] = False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Deep search. Clean draft.</div>
    <h1>
        <span class="deep">Deep</span><span class="draft">Draft</span>
    </h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div class="chip-row">
        <span class="chip-label">TRY →</span>
        <span class="chip">LLM agents 2025</span>
        <span class="chip">CRISPR gene editing</span>
        <span class="chip">Fusion energy progress</span>
    </div>
    """, unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    STEPS = ["search", "reader", "writer", "critic"]
    r = st.session_state.results
    current = st.session_state.current_step

    def get_state(step: str) -> str:
        if step in r:
            return "done"
        if step == current and st.session_state.running:
            return "running"
        return "waiting"

    step_card("01", "Search Agent",  get_state("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  get_state("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  get_state("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  get_state("critic"), "Reviews & scores the report")


# ── Trigger pipeline start ────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.current_step = "search"
        st.rerun()


# ── Execute ONE step per rerun, then rerun again ──────────────────────────────
if st.session_state.running and not st.session_state.done:
    topic_val = st.session_state.topic_input
    r = st.session_state.results
    step = st.session_state.current_step

    if step == "search" and "search" not in r:
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        r["search"] = sr["messages"][-1].content
        st.session_state.results = dict(r)
        st.session_state.current_step = "reader"
        st.rerun()

    elif step == "reader" and "reader" not in r:
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{r['search'][:800]}"
            )]
        })
        r["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(r)
        st.session_state.current_step = "writer"
        st.rerun()

    elif step == "writer" and "writer" not in r:
        research_combined = (
            f"SEARCH RESULTS:\n{r['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{r['reader']}"
        )
        r["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(r)
        st.session_state.current_step = "critic"
        st.rerun()

    elif step == "critic" and "critic" not in r:
        r["critic"] = critic_chain.invoke({
            "report": r["writer"]
        })
        st.session_state.results = dict(r)
        st.session_state.running = False
        st.session_state.done = True
        st.session_state.current_step = None
        st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    DeepDraft · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)