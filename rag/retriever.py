"""
retriever.py – Retrieve the top-k most relevant document chunks.

Uses ``similarity_score_threshold`` search type so that low-confidence results
are filtered out before being passed to the LLM.  Requires the underlying
Chroma collection to be configured with cosine distance (set in vector_store.py).
"""

from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma


def get_retriever(
    vector_store: Chroma,
    top_k: int = 6,
    score_threshold: float = 0.35,
):
    """Return a LangChain retriever for the given vector store.

    Args:
        vector_store: An initialised Chroma vector store (must use cosine
            distance for score normalisation to be meaningful).
        top_k: Maximum number of chunks to retrieve (default 6).
        score_threshold: Minimum relevance score a chunk must have to be
            returned (default 0.35).  Chunks below this threshold are
            discarded so irrelevant context never reaches the LLM.

    Returns:
        A LangChain VectorStoreRetriever using similarity_score_threshold.
    """
    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": top_k, "score_threshold": score_threshold},
    )


def retrieve_chunks(
    vector_store: Chroma,
    query: str,
    top_k: int = 6,
    score_threshold: float = 0.35,
) -> List[Document]:
    """Retrieve the top-k chunks most similar to *query*.

    Results below *score_threshold* are filtered out before returning so that
    callers always receive only high-confidence context.

    Args:
        vector_store: An initialised Chroma vector store.
        query: The student's question.
        top_k: Maximum number of chunks to return (default 6).
        score_threshold: Minimum relevance score to include a chunk
            (default 0.35).

    Returns:
        A list of Document objects ordered by relevance (most relevant first),
        excluding any chunk whose score falls below *score_threshold*.
    """
    results = vector_store.similarity_search_with_relevance_scores(query, k=top_k)
    # Filter by score and return only the Document objects for backward compat.
    return [doc for doc, score in results if score >= score_threshold]
