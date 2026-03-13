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
    page_icon="📚",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar – app status / config
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("📚 LearnIQ")
    st.caption("CBSE Grade 8 Science Tutor")
    st.divider()

    st.subheader("Configuration")
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    top_k = int(os.getenv("TOP_K", "6"))
    chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
    score_threshold = float(os.getenv("SCORE_THRESHOLD", "0.35"))

    st.markdown(f"- **LLM:** `{model_name}`")
    st.markdown(f"- **Embeddings:** `{embedding_model}`")
    st.markdown(f"- **Top-K retrieval:** `{top_k}`")
    st.markdown(f"- **Chunk size:** `{chunk_size}`")
    st.markdown(f"- **Score threshold:** `{score_threshold}`")

    st.divider()

    # API key status
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_set:
        st.success("✅ OpenAI API key loaded")
    else:
        st.error("❌ OPENAI_API_KEY not set")

    # Vector store status
    store_ready = os.path.exists(chroma_dir)
    if store_ready:
        st.success("✅ Vector store ready")
    else:
        st.warning("⚠️ Vector store not found – run the ingestion script first")

    st.divider()

    # Clear chat button
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.previous_query = None
        st.rerun()

    st.caption(
        "Answers are grounded only in the NCERT Grade 8 Science textbook. "
        "No outside knowledge is used."
    )

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("LearnIQ 📖")
st.subheader("Your AI Tutor for CBSE Grade 8 Science")
st.markdown(
    "Ask any question from your **NCERT Grade 8 Science** textbook. "
    "Answers are grounded strictly in the textbook content."
)

# ---------------------------------------------------------------------------
# Session state initialisation (dual state: display + LangChain)
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []          # Display dicts {"role", "content"}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []      # LangChain HumanMessage/AIMessage objects

if "previous_query" not in st.session_state:
    st.session_state.previous_query = None  # Raw text of last question

# ---------------------------------------------------------------------------
# One-time resource initialisation (build chain / embeddings once per session)
# ---------------------------------------------------------------------------

# Guard: only initialise if API key and vector store are both available
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
# Replay chat history (display only; citations not replayed — per plan)
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input & response
# ---------------------------------------------------------------------------

question = st.chat_input("Ask a question from the Grade 8 Science textbook…")

if question:
    # Show the student's message immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        # Guard: API key
        if not os.getenv("OPENAI_API_KEY"):
            error_msg = (
                "⚠️ **OpenAI API key is not configured.**\n\n"
                "Please copy `.env.example` to `.env` and add your `OPENAI_API_KEY`."
            )
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Guard: vector store
        elif not os.path.exists(chroma_dir):
            error_msg = (
                "⚠️ **Textbook index not found.**\n\n"
                "Please run the ingestion script to build the vector store:\n"
                "```\npython scripts/ingest_textbook.py\n```"
            )
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

        else:
            with st.spinner("Searching the textbook…"):
                try:
                    result = ask(
                        chain=st.session_state.rag_chain,
                        question=question,
                        chat_history=st.session_state.chat_history,
                        embeddings_model=st.session_state.embeddings,
                        previous_query=st.session_state.previous_query,
                    )

                    # Show rewritten query transparency (only for follow-up questions)
                    if result["rewritten_query"]:
                        st.info(
                            f"I understood your question as: "
                            f"*{result['rewritten_query']}*"
                        )

                    # Display the answer
                    st.markdown(result["answer"])

                    # Expandable citations (shown only on this turn, not replayed)
                    if result["found"] and result["citations"]:
                        for citation in result["citations"]:
                            with st.expander(
                                f"{citation['chapter']}, Page {citation['page']}",
                                expanded=False,
                            ):
                                st.markdown(f"> {citation['passage']}")

                    # Update display messages (answer text only — no citations in replay)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": result["answer"]}
                    )

                    # Update LangChain history (HumanMessage + AIMessage)
                    st.session_state.chat_history.append(
                        HumanMessage(content=question)
                    )
                    st.session_state.chat_history.append(
                        AIMessage(content=result["answer"])
                    )

                    # Track previous query for next turn's topic-shift check
                    st.session_state.previous_query = question

                except Exception as exc:
                    error_msg = f"⚠️ An error occurred: {exc}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
