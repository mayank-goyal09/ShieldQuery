import streamlit as st
import os
import time
from engine import final_result, process_uploaded_pdf, DB_FAISS_PATH

# ══════════════════════════════════════════════════════════════
# Page Configuration
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# Custom CSS — Premium Dark Theme
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Import Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-primary: #0f1117;
        --bg-secondary: #1a1d29;
        --bg-card: #1e2233;
        --bg-card-hover: #252a3e;
        --accent-primary: #6c5ce7;
        --accent-secondary: #a29bfe;
        --accent-glow: rgba(108, 92, 231, 0.15);
        --text-primary: #e8e8f0;
        --text-secondary: #a0a0b8;
        --text-muted: #6b6b80;
        --border-color: rgba(108, 92, 231, 0.2);
        --success: #00cec9;
        --warning: #fdcb6e;
        --danger: #ff6b6b;
        --gradient-1: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        --gradient-2: linear-gradient(135deg, #0f1117 0%, #1a1d29 100%);
    }

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Main header ── */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .main-header h1 {
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 300;
    }

    /* ── Divider ── */
    .gradient-divider {
        height: 2px;
        background: var(--gradient-1);
        border: none;
        border-radius: 2px;
        margin: 0.5rem 0 1.5rem;
        opacity: 0.5;
    }

    /* ── Status badges ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-ready {
        background: rgba(0, 206, 201, 0.12);
        color: #00cec9;
        border: 1px solid rgba(0, 206, 201, 0.25);
    }
    .status-waiting {
        background: rgba(253, 203, 110, 0.12);
        color: #fdcb6e;
        border: 1px solid rgba(253, 203, 110, 0.25);
    }

    /* ── Insight cards ── */
    .insight-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    .insight-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--accent-secondary);
        transform: translateX(3px);
    }
    .insight-card .icon { font-size: 1.1rem; margin-right: 8px; }
    .insight-card .text {
        color: var(--text-primary);
        font-size: 0.88rem;
        font-weight: 400;
    }

    /* ── Stats row ── */
    .stats-container {
        display: flex;
        gap: 10px;
        margin: 1rem 0;
    }
    .stat-box {
        flex: 1;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 12px 14px;
        text-align: center;
    }
    .stat-box .number {
        font-size: 1.4rem;
        font-weight: 700;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-box .label {
        color: var(--text-muted);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* ── Chat messages ── */
    .chat-message {
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        line-height: 1.65;
        font-size: 0.92rem;
        animation: fadeIn 0.3s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-msg {
        background: linear-gradient(135deg, rgba(108, 92, 231, 0.15), rgba(162, 155, 254, 0.08));
        border: 1px solid rgba(108, 92, 231, 0.25);
        color: var(--text-primary);
    }
    .assistant-msg {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    .msg-role {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 6px;
    }
    .msg-role-user { color: var(--accent-secondary); }
    .msg-role-assistant { color: var(--success); }

    .source-tag {
        display: inline-block;
        margin-top: 10px;
        padding: 4px 10px;
        border-radius: 6px;
        background: rgba(108, 92, 231, 0.1);
        border: 1px solid rgba(108, 92, 231, 0.2);
        color: var(--text-muted);
        font-size: 0.72rem;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary) !important;
    }

    /* ── Upload area ── */
    .upload-zone {
        border: 2px dashed var(--border-color);
        border-radius: 14px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    .upload-zone:hover {
        border-color: var(--accent-primary);
        background: var(--accent-glow);
    }

    /* ── Welcome panel ── */
    .welcome-panel {
        text-align: center;
        padding: 3rem 2rem;
        max-width: 600px;
        margin: 2rem auto;
    }
    .welcome-panel .emoji { font-size: 3rem; margin-bottom: 1rem; }
    .welcome-panel h2 {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .welcome-panel p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.7;
    }

    /* ── Feature cards grid ── */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-top: 1.5rem;
    }
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        border-color: var(--accent-primary);
        box-shadow: 0 8px 25px var(--accent-glow);
    }
    .feature-card .f-icon { font-size: 1.8rem; margin-bottom: 8px; }
    .feature-card .f-title {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }
    .feature-card .f-desc {
        color: var(--text-muted);
        font-size: 0.75rem;
        line-height: 1.5;
    }

    /* ── Streamlit overrides ── */
    .stChatInput > div {
        border-color: var(--border-color) !important;
        border-radius: 12px !important;
    }
    .stChatInput > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# Session State Initialization
# ══════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_insights" not in st.session_state:
    st.session_state.doc_insights = []
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = {"pages": 0, "chunks": 0, "files": 0}
if "documents_loaded" not in st.session_state:
    # Check if a vector store already exists from a previous session
    st.session_state.documents_loaded = os.path.exists(
        os.path.join(DB_FAISS_PATH, "index.faiss")
    )


# ══════════════════════════════════════════════════════════════
# Sidebar — Document Upload & Insights
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📄 Document Center")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Upload Section ──
    uploaded_file = st.file_uploader(
        "Upload Document (PDF)",
        type=["pdf"],
        help="Upload any text-based PDF — assignments, NDAs, contracts, policies, reports, and more.",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        # Prevent re-processing the same file
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("last_uploaded_file") != file_key:
            with st.spinner("🔍 Analyzing document..."):
                file_bytes = uploaded_file.read()
                result = process_uploaded_pdf(file_bytes, uploaded_file.name)

            if result["success"]:
                st.success(f"✅ {result['message']}")
                st.session_state.doc_insights = result["insights"]
                st.session_state.doc_stats["pages"] += result["page_count"]
                st.session_state.doc_stats["chunks"] += result["chunk_count"]
                st.session_state.doc_stats["files"] += 1
                st.session_state.documents_loaded = True
                st.session_state.last_uploaded_file = file_key
            else:
                st.warning(result["message"])

    # ── Status ──
    st.markdown("#### System Status")
    if st.session_state.documents_loaded:
        st.markdown(
            '<span class="status-badge status-ready">● Ready to Analyze</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-waiting">● Awaiting Document</span>',
            unsafe_allow_html=True,
        )

    # ── Document Stats ──
    if st.session_state.doc_stats["files"] > 0:
        stats = st.session_state.doc_stats
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="number">{stats['files']}</div>
                <div class="label">Documents</div>
            </div>
            <div class="stat-box">
                <div class="number">{stats['pages']}</div>
                <div class="label">Pages</div>
            </div>
            <div class="stat-box">
                <div class="number">{stats['chunks']}</div>
                <div class="label">Chunks</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Insights Panel ──
    if st.session_state.doc_insights:
        st.markdown("#### 💡 Key Topics Detected")
        icons = ["📋", "📑", "📅", "�", "👥", "⚖️", "🎓", "🔒"]
        for i, insight in enumerate(st.session_state.doc_insights):
            icon = icons[i % len(icons)]
            st.markdown(f"""
            <div class="insight-card">
                <span class="icon">{icon}</span>
                <span class="text">{insight}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Actions ──
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        '<p style="color: var(--text-muted); font-size: 0.7rem; text-align: center; '
        'margin-top: 2rem;">Document Intelligence v2.0<br>Powered by LLaMA 3.3</p>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════
# Main Area — Header
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🔍 Document Intelligence</h1>
    <p>Upload any document — assignments, NDAs, contracts, policies — and get instant AI-powered analysis</p>
</div>
<div class="gradient-divider"></div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# Welcome state (no messages yet)
# ══════════════════════════════════════════════════════════════
if not st.session_state.messages:
    if not st.session_state.documents_loaded:
        st.markdown("""
        <div class="welcome-panel">
            <div class="emoji">📤</div>
            <h2>Upload a Document to Begin</h2>
            <p>
                Use the sidebar to upload any PDF document — assignments, contracts, 
                NDAs, company policies, reports, or memos. I'll analyze it and you 
                can ask me anything about its contents.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-panel">
            <div class="emoji">🤖</div>
            <h2>Documents Ready — Ask Away!</h2>
            <p>
                Your documents have been analyzed. Ask me anything about the 
                content, clauses, requirements, or any information contained in them.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="f-icon">📑</div>
            <div class="f-title">Document Analysis</div>
            <div class="f-desc">Analyze assignments, contracts, NDAs, policies & more</div>
        </div>
        <div class="feature-card">
            <div class="f-icon">💡</div>
            <div class="f-title">Smart Insights</div>
            <div class="f-desc">Auto-detected key topics and sections from your documents</div>
        </div>
        <div class="feature-card">
            <div class="f-icon">🛡️</div>
            <div class="f-title">Accurate Answers</div>
            <div class="f-desc">Grounded entirely in your uploaded documents — no fabrication</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# Chat History Display
# ══════════════════════════════════════════════════════════════
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    source = msg.get("source", "")

    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-msg">
            <div class="msg-role msg-role-user">You</div>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        source_html = (
            f'<div class="source-tag">📎 Source: {source}</div>' if source else ""
        )
        st.markdown(f"""
        <div class="chat-message assistant-msg">
            <div class="msg-role msg-role-assistant">Document Analyst</div>
            {content}
            {source_html}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# Chat Input
# ══════════════════════════════════════════════════════════════
if prompt := st.chat_input("Ask anything about your uploaded documents..."):
    # ── Show user message ──
    st.markdown(f"""
    <div class="chat-message user-msg">
        <div class="msg-role msg-role-user">You</div>
        {prompt}
    </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ── Get AI response ──
    with st.spinner("🔍 Searching documents..."):
        response = final_result(prompt)

    answer = response["result"]
    source_name = ""

    # Try to extract source filename
    try:
        source_docs = response.get("source_documents", [])
        if source_docs:
            raw_source = source_docs[0].metadata.get("source", "")
            source_name = os.path.basename(raw_source) if raw_source else ""
    except Exception:
        source_name = ""

    source_html = (
        f'<div class="source-tag">📎 Source: {source_name}</div>' if source_name else ""
    )
    st.markdown(f"""
    <div class="chat-message assistant-msg">
        <div class="msg-role msg-role-assistant">Document Analyst</div>
        {answer}
        {source_html}
    </div>
    """, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "source": source_name,
    })