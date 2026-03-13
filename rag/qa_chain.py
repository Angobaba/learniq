"""
qa_chain.py – Generate a grounded answer from retrieved document chunks.
"""

import os
from typing import Dict, List

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from rag.prompts import SYSTEM_PROMPT, NO_CONTEXT_RESPONSE


def _format_context(chunks: List[Document]) -> str:
    """Format retrieved chunks into a single context string with citations."""
    parts = []
    for i, doc in enumerate(chunks, start=1):
        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", "?")
        parts.append(f"[{i}] (Source: {source}, Page: {page})\n{doc.page_content}")
    return "\n\n".join(parts)


def _extract_citations(chunks: List[Document]) -> List[Dict]:
    """Return a deduplicated list of citation dicts from chunk metadata."""
    seen = set()
    citations = []
    for doc in chunks:
        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", "?")
        key = (source, page)
        if key not in seen:
            seen.add(key)
            citations.append({"source": source, "page": page})
    return citations


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


def answer_question(
    question: str,
    chunks: List[Document],
    llm: ChatOpenAI | None = None,
) -> Dict:
    """Generate a grounded answer given a question and retrieved chunks.

    Args:
        question: The student's question.
        chunks: Retrieved document chunks from the vector store.
        llm: An optional pre-built ChatOpenAI instance.  Created on-demand
            if not supplied.

    Returns:
        A dict with keys:
            - ``answer``    (str)  the grounded answer text
            - ``citations`` (list) list of {"source": ..., "page": ...} dicts
            - ``found``     (bool) True if relevant context was retrieved
    """
    if not chunks:
        return {
            "answer": NO_CONTEXT_RESPONSE,
            "citations": [],
            "found": False,
        }

    if llm is None:
        llm = build_qa_chain()

    context = _format_context(chunks)
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=SYSTEM_PROMPT,
    )
    formatted_prompt = prompt.format(context=context, question=question)

    response = llm.invoke(formatted_prompt)
    answer_text = response.content.strip()

    citations = _extract_citations(chunks)

    return {
        "answer": answer_text,
        "citations": citations,
        "found": True,
    }
