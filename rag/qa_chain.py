"""
qa_chain.py – Conversational RAG chain with query rewriting and topic-shift detection.

Provides:
  - build_conversational_chain(vector_store) -> LangChain retrieval chain
  - ask(chain, question, chat_history, embeddings_model, previous_query) -> dict
  - detect_topic_shift(current_query, previous_query, embeddings, threshold) -> bool
  - build_qa_chain() -> ChatOpenAI   (kept for backward compat / LLM access)
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import numpy as np
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from rag.embeddings import get_embeddings
from rag.prompts import REWRITE_SYSTEM, SYSTEM_PROMPT, NO_CONTEXT_RESPONSE
from rag.retriever import get_retriever


# ---------------------------------------------------------------------------
# LLM builder (kept for callers that only need the raw LLM)
# ---------------------------------------------------------------------------


def build_qa_chain(model_name: str | None = None) -> ChatOpenAI:
    """Build and return a ChatOpenAI LLM instance.

    Args:
        model_name: OpenAI model to use.  Defaults to the MODEL_NAME
            environment variable (or gpt-4o-mini).

    Returns:
        A ChatOpenAI instance.

    Raises:
        ValueError: If OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Please copy .env.example to .env and add your API key."
        )

    if model_name is None:
        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

    return ChatOpenAI(model=model_name, openai_api_key=api_key, temperature=0)


# ---------------------------------------------------------------------------
# Topic shift detection
# ---------------------------------------------------------------------------


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Return the cosine similarity between two embedding vectors."""
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def detect_topic_shift(
    current_query: str,
    previous_query: Optional[str],
    embeddings,
    threshold: float = 0.3,
) -> bool:
    """Return True when the current question is on a different topic.

    Compares the two queries by cosine similarity of their embeddings.
    A similarity below *threshold* is treated as a topic shift.

    Args:
        current_query:  The latest student question.
        previous_query: The immediately preceding question, or None.
        embeddings:     An OpenAIEmbeddings instance (or compatible).
        threshold:      Similarity cutoff below which a shift is declared.

    Returns:
        True if a topic shift is detected, False otherwise.
    """
    if not previous_query:
        return False

    vecs = embeddings.embed_documents([current_query, previous_query])
    return _cosine_similarity(vecs[0], vecs[1]) < threshold


# ---------------------------------------------------------------------------
# Citation extraction
# ---------------------------------------------------------------------------


def _extract_citations(docs: List[Document], max_citations: int = 2) -> List[Dict]:
    """Return up to *max_citations* citation dicts from retrieved documents.

    Deduplicates by (chapter, page) so the same source is not listed twice.

    Returns:
        List of dicts with keys: chapter, page, passage.
    """
    seen: set = set()
    citations: List[Dict] = []

    for doc in docs:
        chapter = doc.metadata.get("chapter", "Unknown Chapter")
        page = doc.metadata.get("page", "?")
        key = (chapter, page)
        if key not in seen:
            seen.add(key)
            citations.append(
                {
                    "chapter": chapter,
                    "page": page,
                    "passage": doc.page_content.strip()[:600],  # trim very long passages
                }
            )
        if len(citations) >= max_citations:
            break

    return citations


# ---------------------------------------------------------------------------
# Conversational chain builder
# ---------------------------------------------------------------------------


def build_conversational_chain(vector_store):
    """Build a history-aware conversational retrieval chain.

    Args:
        vector_store: An initialised Chroma vector store (cosine distance).

    Returns:
        A LangChain create_retrieval_chain chain ready to be invoked with
        {"input": question, "chat_history": [HumanMessage, AIMessage, ...]}.
    """
    llm = build_qa_chain()
    base_retriever = get_retriever(vector_store)

    # --- Rewrite prompt: reformulate follow-up questions into standalone queries ---
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REWRITE_SYSTEM),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_retriever = create_history_aware_retriever(llm, base_retriever, rewrite_prompt)

    # --- Answer prompt: grounded answer with inline citations ---
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    combine_docs_chain = create_stuff_documents_chain(llm, answer_prompt)
    return create_retrieval_chain(history_retriever, combine_docs_chain)


# ---------------------------------------------------------------------------
# Main entry-point for asking questions
# ---------------------------------------------------------------------------


def ask(
    chain,
    question: str,
    chat_history: List,
    embeddings_model,
    previous_query: Optional[str] = None,
) -> Dict:
    """Ask a question using the conversational chain.

    Handles topic-shift detection (zeroes out history on shift),
    runs a separate rewrite step to surface the reformulated query,
    and extracts structured citations from the retrieved documents.

    Args:
        chain:           The chain returned by build_conversational_chain().
        question:        The current student question.
        chat_history:    List of HumanMessage/AIMessage objects (LangChain format).
        embeddings_model: OpenAIEmbeddings instance for topic-shift cosine check.
        previous_query:  The immediately preceding raw question (for shift detection).

    Returns:
        Dict with keys:
            answer          (str)  – The LLM answer text.
            citations       (list) – List of {chapter, page, passage} dicts (max 2).
            found           (bool) – False when no context docs were retrieved.
            context_docs    (list) – Raw Document objects from retriever.
            rewritten_query (str|None) – Rewritten query shown to student, or None
                                         if this was the first question / topic shift.
    """
    # Detect topic shift — if detected, drop old history to prevent contamination
    is_topic_shift = detect_topic_shift(question, previous_query, embeddings_model)
    effective_history = [] if is_topic_shift else chat_history

    # For follow-up questions with non-empty history, surface the rewritten query
    rewritten_query: Optional[str] = None
    if effective_history and previous_query:
        # Run just the rewrite prompt + LLM to capture what the retriever will search
        llm = build_qa_chain()
        rewrite_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", REWRITE_SYSTEM),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        rewrite_chain = rewrite_prompt | llm
        rewrite_result = rewrite_chain.invoke(
            {"input": question, "chat_history": effective_history}
        )
        candidate = rewrite_result.content.strip()
        # Only show if the rewrite actually changed the question
        if candidate.lower() != question.lower():
            rewritten_query = candidate

    # Invoke the full retrieval chain
    result = chain.invoke({"input": question, "chat_history": effective_history})

    answer: str = result.get("answer", NO_CONTEXT_RESPONSE)
    context_docs: List[Document] = result.get("context", [])

    found = bool(context_docs)
    citations = _extract_citations(context_docs) if found else []

    return {
        "answer": answer,
        "citations": citations,
        "found": found,
        "context_docs": context_docs,
        "rewritten_query": rewritten_query,
    }
