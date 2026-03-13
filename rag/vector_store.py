"""
vector_store.py – Create or load a ChromaDB persistent vector store.
"""

import os
from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma

from rag.embeddings import get_embeddings

COLLECTION_NAME = "learniq_textbook"


def build_vector_store(
    chunks: List[Document],
    persist_dir: str | None = None,
) -> Chroma:
    """Embed a list of document chunks and persist them in ChromaDB.

    If a store already exists at *persist_dir* it will be overwritten.

    Args:
        chunks: List of chunked Document objects to embed and store.
        persist_dir: Directory where ChromaDB will persist data.  Defaults to
            the CHROMA_PERSIST_DIR environment variable (or ./chroma_db).

    Returns:
        A Chroma vector store instance.
    """
    if persist_dir is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=persist_dir,
    )
    return vector_store


def load_vector_store(persist_dir: str | None = None) -> Chroma:
    """Load an existing ChromaDB vector store from disk.

    Args:
        persist_dir: Directory where ChromaDB data was persisted.

    Returns:
        A Chroma vector store instance.

    Raises:
        FileNotFoundError: If the persist directory does not exist, indicating
            that the ingestion script has not been run yet.
    """
    if persist_dir is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"ChromaDB store not found at: {persist_dir}\n"
            "Please run the ingestion script first:\n"
            "    python scripts/ingest_textbook.py"
        )

    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )
    return vector_store
