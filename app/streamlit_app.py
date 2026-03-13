"""
streamlit_app.py – LearnIQ main chat interface.

Run with:
    streamlit run app/streamlit_app.py
"""

import os
import sys

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# Load .env if present
load_dotenv()

# Allow imports from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.vector_store import load_vector_store
from rag.embeddings import get_embeddings
from rag.qa_chain import build_conversational_chain, ask

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="LearnIQ – CBSE Grade 8 Science Tutor",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS – dark gradient UI inspired by modern AI chat apps
# ---------------------------------------------------------------------------

st.markdown("""
<style>
/* ── Import Google Fonts ───────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ────────────────────────────────────── */
:root {
    --bg-primary: #0B0716;
    --bg-secondary: #130E24;
    --bg-card: rgba(26, 19, 51, 0.65);
    --bg-card-border: rgba(124, 58, 237, 0.15);
    --purple-500: #7C3AED;
    --purple-400: #A78BFA;
    --purple-300: #C4B5FD;
    --purple-600: #5B21B6;
    --purple-700: #4C1D95;
    --blue-400: #60A5FA;
    --blue-500: #3B82F6;
    --pink-400: #F472B6;
    --text-primary: #F1EEFB;
    --text-secondary: #A8A0C0;
    --text-muted: #6B6187;
    --user-bubble: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
    --assistant-bubble: rgba(26, 19, 51, 0.8);
    --input-bg: rgba(19, 14, 36, 0.9);
    --input-border: rgba(124, 58, 237, 0.3);
    --glow-purple: rgba(124, 58, 237, 0.15);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-pill: 9999px;
}

/* ── Global resets ─────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Full-page gradient background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        180deg,
        #0B0716 0%,
        #130E24 30%,
        #1A1040 60%,
        #0F0D2E 100%
    ) !important;
}

/* Aurora glow effect at top */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 400px;
    background: radial-gradient(
        ellipse at center,
        rgba(124, 58, 237, 0.18) 0%,
        rgba(99, 102, 241, 0.08) 40%,
        transparent 70%
    );
    pointer-events: none;
    z-index: 0;
}

/* Second glow orb – pink/blue */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    top: 60px;
    right: 10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(
        ellipse at center,
        rgba(244, 114, 182, 0.08) 0%,
        rgba(96, 165, 250, 0.05) 50%,
        transparent 70%
    );
    pointer-events: none;
    z-index: 0;
}

/* Remove Streamlit's default header/footer */
header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer, [data-testid="stDecoration"] {
    display: none !important;
}

/* Hide default Streamlit top padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0 !important;
    max-width: 780px !important;
}

/* ── Sidebar (minimal) ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F0A1E 0%, #1A1040 100%) !important;
    border-right: 1px solid rgba(124, 58, 237, 0.12) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: var(--text-secondary) !important;
}

/* ── Custom header area ────────────────────────────────── */
div.app-header {
    text-align: center;
    padding: 1.5rem 1rem 0.5rem 1rem;
    position: relative;
    z-index: 1;
}

div.app-header .logo-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: linear-gradient(135deg, #7C3AED 0%, #3B82F6 100%);
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
    margin-bottom: 12px;
    font-size: 26px;
}

div.app-header h1 {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.3px;
    line-height: 1.3;
}

div.app-header .subtitle {
    font-size: 13px;
    color: var(--text-secondary);
    font-weight: 400;
    margin: 0;
    line-height: 1.5;
}

/* ── Greeting card (shown when no messages) ────────────── */
div.greeting-card {
    background: var(--bg-card);
    border: 1px solid var(--bg-card-border);
    border-radius: var(--radius-xl);
    padding: 28px 24px;
    margin: 20px auto 16px auto;
    max-width: 520px;
    text-align: center;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: relative;
    z-index: 1;
}

div.greeting-card h2 {
    font-size: 20px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    margin: 0 0 6px 0 !important;
}

div.greeting-card p {
    font-size: 13.5px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.55;
}

/* ── Suggestion chips ──────────────────────────────────── */
div.suggestion-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin: 18px auto 8px auto;
    max-width: 560px;
    position: relative;
    z-index: 1;
}

/* ── Chat messages ─────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 6px 0 !important;
    gap: 10px !important;
}

/* User avatar */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #7C3AED, #5B21B6) !important;
    border-radius: 50% !important;
}

/* Assistant avatar */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #3B82F6, #6366F1) !important;
    border-radius: 50% !important;
}

/* User message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
    background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
    border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg) !important;
    padding: 12px 16px !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
    line-height: 1.55 !important;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.2);
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child p {
    color: #FFFFFF !important;
}

/* Assistant message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
    background: rgba(26, 19, 51, 0.75) !important;
    border: 1px solid rgba(124, 58, 237, 0.12) !important;
    border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px !important;
    padding: 14px 18px !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

/* ── Chat input ────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

[data-testid="stChatInput"] > div {
    background: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: var(--radius-pill) !important;
    padding: 4px 8px !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(124, 58, 237, 0.08) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--purple-500) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), 0 0 0 3px rgba(124, 58, 237, 0.12) !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    caret-color: var(--purple-400) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
    font-size: 14px !important;
}

/* Send button in chat input */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
    border: none !important;
    border-radius: 50% !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(124, 58, 237, 0.3) !important;
}

[data-testid="stChatInput"] button:hover {
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.45) !important;
}

/* ── Expander (citations) ──────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(19, 14, 36, 0.6) !important;
    border: 1px solid rgba(124, 58, 237, 0.12) !important;
    border-radius: var(--radius-md) !important;
    margin-top: 6px !important;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    font-size: 12.5px !important;
    font-weight: 500 !important;
    color: var(--purple-300) !important;
    padding: 8px 14px !important;
}

[data-testid="stExpander"] summary:hover {
    color: var(--purple-400) !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    border-top: 1px solid rgba(124, 58, 237, 0.08) !important;
    padding: 10px 14px !important;
}

[data-testid="stExpander"] blockquote {
    border-left: 3px solid var(--purple-600) !important;
    background: rgba(124, 58, 237, 0.06) !important;
    padding: 10px 14px !important;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
    font-size: 12.5px !important;
    line-height: 1.6 !important;
    color: var(--text-secondary) !important;
}

/* ── Info box (rewritten query) ────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(96, 165, 250, 0.08) !important;
    border: 1px solid rgba(96, 165, 250, 0.15) !important;
    border-radius: var(--radius-md) !important;
    color: var(--blue-400) !important;
    font-size: 12.5px !important;
    padding: 10px 14px !important;
    backdrop-filter: blur(8px) !important;
}

[data-testid="stAlert"] p {
    color: var(--blue-400) !important;
    font-size: 12.5px !important;
}

/* Error alerts */
[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: var(--radius-md) !important;
}

/* ── Spinner ───────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--purple-400) !important;
}

[data-testid="stSpinner"] > div {
    border-color: var(--purple-500) transparent transparent transparent !important;
}

/* ── Buttons (sidebar + suggestion chips) ──────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    border-radius: var(--radius-pill) !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(124, 58, 237, 0.12) !important;
    border: 1px solid rgba(124, 58, 237, 0.2) !important;
    color: var(--purple-300) !important;
    padding: 8px 20px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124, 58, 237, 0.22) !important;
    border-color: rgba(124, 58, 237, 0.35) !important;
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.2);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(124, 58, 237, 0.35);
}

/* ── Bottom padding for chat input ─────────────────────── */
[data-testid="stBottom"] {
    background: linear-gradient(180deg, transparent 0%, var(--bg-primary) 30%) !important;
    padding-top: 20px !important;
}

[data-testid="stBottom"] > div {
    max-width: 780px !important;
}

/* ── Divider ───────────────────────────────────────────── */
hr {
    border-color: rgba(124, 58, 237, 0.1) !important;
}

/* ── Sidebar caption/text tweaks ───────────────────────── */
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
    color: var(--text-muted) !important;
    font-size: 11.5px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Env / config (hidden from UI)
# ---------------------------------------------------------------------------

chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# ---------------------------------------------------------------------------
# Sidebar – minimal, student-friendly
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <div style="display:inline-flex; align-items:center; justify-content:center;
                    width:44px; height:44px; border-radius:12px;
                    background:linear-gradient(135deg,#7C3AED,#3B82F6);
                    box-shadow: 0 4px 16px rgba(124,58,237,0.3);
                    font-size:22px; margin-bottom:8px;">
            📖
        </div>
        <h3 style="margin:0; font-size:17px; font-weight:600; color:#F1EEFB;">LearnIQ</h3>
        <p style="margin:2px 0 0 0; font-size:12px; color:#A8A0C0;">CBSE Grade 8 Science</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Chapter quick links
    st.markdown("""
    <p style="font-size:12px; font-weight:600; color:#A8A0C0; text-transform:uppercase;
              letter-spacing:0.8px; margin-bottom:8px;">Quick Topics</p>
    """, unsafe_allow_html=True)

    topic_selected = None
    topic_cols = st.columns(2)
    topics = [
        ("🔬", "Microorganisms"),
        ("🌱", "Crop Production"),
        ("🧪", "Synthetic Fibres"),
        ("⚡", "Chemical Effects"),
        ("🔥", "Combustion"),
        ("💡", "Light"),
        ("⭐", "Stars & Solar System"),
        ("🌀", "Force & Pressure"),
        ("🔊", "Sound"),
        ("🧲", "Friction"),
    ]
    for i, (icon, topic) in enumerate(topics):
        col = topic_cols[i % 2]
        with col:
            if st.button(f"{icon} {topic}", key=f"topic_{i}", use_container_width=True):
                topic_selected = topic

    st.divider()

    if st.button("🗑  New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.previous_query = None
        st.rerun()

    st.caption("Answers are grounded only in the NCERT Grade 8 Science textbook.")

# ---------------------------------------------------------------------------
# App header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="app-header">
    <div class="logo-icon">📖</div>
    <h1>LearnIQ</h1>
    <p class="subtitle">Your AI Science Tutor for CBSE Grade 8</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "previous_query" not in st.session_state:
    st.session_state.previous_query = None

# ---------------------------------------------------------------------------
# One-time resource initialisation
# ---------------------------------------------------------------------------

_can_init = bool(os.getenv("OPENAI_API_KEY")) and os.path.exists(chroma_dir)

if _can_init:
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = load_vector_store()

    if "embeddings" not in st.session_state:
        st.session_state.embeddings = get_embeddings()

    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = build_conversational_chain(
            st.session_state.vector_store
        )

# ---------------------------------------------------------------------------
# Greeting screen (shown when no messages)
# ---------------------------------------------------------------------------

SUGGESTED_QUESTIONS = [
    "What is friction?",
    "Explain photosynthesis",
    "Types of microorganisms",
    "What is combustion?",
    "How does sound travel?",
    "What are synthetic fibres?",
]

if not st.session_state.messages:
    st.markdown("""
    <div class="greeting-card">
        <h2>Hi there! 👋</h2>
        <p>Ask me anything about your NCERT Grade 8 Science textbook.
           I'll find the answer and show you exactly where it's from.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="suggestion-grid">', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
                topic_selected = q
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Replay chat history
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input & response
# ---------------------------------------------------------------------------

# Handle topic button clicks from sidebar or suggestions
if topic_selected:
    question = f"Tell me about {topic_selected}" if len(topic_selected.split()) <= 2 else topic_selected
else:
    question = st.chat_input("Ask a question about Grade 8 Science...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if not os.getenv("OPENAI_API_KEY"):
            error_msg = "I'm not fully set up yet. Please ask your teacher to configure the system."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        elif not os.path.exists(chroma_dir):
            error_msg = "The textbook hasn't been loaded yet. Please ask your teacher to set it up."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        else:
            with st.spinner("Looking through your textbook..."):
                try:
                    result = ask(
                        chain=st.session_state.rag_chain,
                        question=question,
                        chat_history=st.session_state.chat_history,
                        embeddings_model=st.session_state.embeddings,
                        previous_query=st.session_state.previous_query,
                    )

                    if result["rewritten_query"]:
                        st.info(
                            f"I understood your question as: "
                            f"*{result['rewritten_query']}*"
                        )

                    st.markdown(result["answer"])

                    if result["found"] and result["citations"]:
                        for citation in result["citations"]:
                            source_label = citation.get("source_name", "")
                            if source_label:
                                label = f"📄 {source_label} — {citation['chapter']}, Page {citation['page']}"
                            else:
                                label = f"📄 {citation['chapter']}, Page {citation['page']}"
                            with st.expander(label, expanded=False):
                                st.markdown(f"> {citation['passage']}")

                    st.session_state.messages.append(
                        {"role": "assistant", "content": result["answer"]}
                    )

                    st.session_state.chat_history.append(
                        HumanMessage(content=question)
                    )
                    st.session_state.chat_history.append(
                        AIMessage(content=result["answer"])
                    )

                    st.session_state.previous_query = question

                except Exception as exc:
                    error_msg = "Something went wrong. Please try asking again."
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
