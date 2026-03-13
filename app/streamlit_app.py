"""
streamlit_app.py – LearnIQ main chat interface.

Run with:
    streamlit run app/streamlit_app.py
"""

import os
import sys

import streamlit as st
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Allow imports from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.vector_store import load_vector_store
from rag.retriever import retrieve_chunks
from rag.qa_chain import build_qa_chain, answer_question

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
    top_k = int(os.getenv("TOP_K", "4"))
    chunk_size = int(os.getenv("CHUNK_SIZE", "500"))

    st.markdown(f"- **LLM:** `{model_name}`")
    st.markdown(f"- **Embeddings:** `{embedding_model}`")
    st.markdown(f"- **Top-K retrieval:** `{top_k}`")
    st.markdown(f"- **Chunk size:** `{chunk_size}`")

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
# Session state for chat history
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Input & response
# ---------------------------------------------------------------------------

question = st.chat_input("Ask a question from the Grade 8 Science textbook…")

if question:
    # Show the student's message
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
                    vector_store = load_vector_store()
                    chunks = retrieve_chunks(vector_store, question)
                    llm = build_qa_chain()
                    result = answer_question(question, chunks, llm)

                    answer = result["answer"]
                    citations = result["citations"]
                    found = result["found"]

                    st.markdown(answer)

                    if found and citations:
                        st.divider()
                        st.markdown("**📌 Sources:**")
                        for c in citations:
                            source = os.path.basename(c["source"])
                            page = c["page"]
                            st.markdown(f"- `{source}` — Page {page}")

                    full_response = answer
                    if found and citations:
                        full_response += "\n\n**📌 Sources:**\n"
                        for c in citations:
                            source = os.path.basename(c["source"])
                            full_response += f"- `{source}` — Page {c['page']}\n"

                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )

                except Exception as exc:
                    error_msg = f"⚠️ An error occurred: {exc}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
