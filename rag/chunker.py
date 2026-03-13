"""
chunker.py – Split loaded Documents into smaller chunks for embedding.
"""

import os
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(
    documents: List[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Document]:
    """Split a list of Documents into smaller overlapping chunks.

    Chunk size and overlap are read from environment variables if not supplied
    explicitly:
        CHUNK_SIZE    (default: 500)
        CHUNK_OVERLAP (default: 50)

    Args:
        documents: List of Document objects to split.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        A flat list of chunked Document objects, each preserving the metadata of
        its parent document (source, page).
    """
    if chunk_size is None:
        chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
    if chunk_overlap is None:
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(documents)
    return chunks
