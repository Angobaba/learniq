"""
retriever.py – Retrieve the top-k most relevant document chunks.
"""

import os
from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma


def get_retriever(vector_store: Chroma, top_k: int | None = None):
    """Return a LangChain retriever for the given vector store.

    Args:
        vector_store: An initialised Chroma vector store.
        top_k: Number of top chunks to retrieve.  Defaults to the TOP_K
            environment variable (or 4).

    Returns:
        A LangChain VectorStoreRetriever.
    """
    if top_k is None:
        top_k = int(os.getenv("TOP_K", "4"))

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )


def retrieve_chunks(
    vector_store: Chroma,
    query: str,
    top_k: int | None = None,
) -> List[Document]:
    """Retrieve the top-k chunks most similar to *query*.

    Args:
        vector_store: An initialised Chroma vector store.
        query: The student's question.
        top_k: Number of chunks to return.

    Returns:
        A list of Document objects ordered by relevance (most relevant first).
    """
    if top_k is None:
        top_k = int(os.getenv("TOP_K", "4"))

    return vector_store.similarity_search(query, k=top_k)
