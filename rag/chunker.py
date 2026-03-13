"""
chunker.py – Split loaded Documents into smaller chunks for embedding.

Uses token-based splitting (tiktoken / gpt-4o-mini token counts) so chunks
stay within model context limits.  Documents are first grouped by chapter so
that no chunk ever crosses a chapter boundary.
"""

import re
import unicodedata
from typing import Dict, List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Regex to detect chapter headings anywhere in the first 500 chars of a page.
# Matches patterns like:
#   "Chapter 1 – Motion and Measurement"
#   "Chapter 12: Friction"
#   "CHAPTER 3 - Fibre to Fabric"
_CHAPTER_RE = re.compile(
    r"Chapter\s+\d+[\s\-\u2013:]+(.+)",
    re.IGNORECASE,
)


def build_chapter_map(documents: List[Document]) -> Dict[int, str]:
    """Scan page documents and return a mapping of page_number -> chapter_name.

    Pages that do not contain a chapter heading inherit the most recently seen
    chapter name.  Pages before the first chapter heading are mapped to
    "Unknown Chapter".

    Args:
        documents: List of Document objects loaded from a PDF (one per page).
            Each document's metadata is expected to contain a ``page`` key
            (0-based or 1-based – we use whatever value is stored).

    Returns:
        A dict mapping ``page_number`` (int) -> ``chapter_name`` (str).
    """
    chapter_map: Dict[int, str] = {}
    current_chapter = "Unknown Chapter"

    for doc in documents:
        page_num = doc.metadata.get("page", 0)
        sample = doc.page_content[:500]
        match = _CHAPTER_RE.search(sample)
        if match:
            # Clean up trailing whitespace / page numbers from the heading.
            # Normalize Unicode (PDF text often contains thin spaces, etc.)
            heading = match.group(1).strip()
            heading = " ".join(heading.split())  # collapse all whitespace variants
            heading = unicodedata.normalize("NFKC", heading)
            # Rebuild full label, e.g. "Chapter 12: Friction"
            chapter_num_match = re.search(r"Chapter\s+(\d+)", sample, re.IGNORECASE)
            if chapter_num_match:
                current_chapter = f"Chapter {chapter_num_match.group(1)}: {heading}"
            else:
                current_chapter = heading
        chapter_map[page_num] = current_chapter

    return chapter_map


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Document]:
    """Split a list of Documents into smaller overlapping chunks.

    Documents are first grouped by chapter (using the chapter map built from
    the PDF pages), split independently per chapter so no chunk ever spans
    two chapters, then metadata (``chapter`` and ``page``) is attached to
    every resulting chunk.

    Args:
        documents: List of Document objects to split.
        chunk_size: Maximum number of tokens per chunk (default 800).
        chunk_overlap: Number of overlapping tokens between consecutive chunks
            (default 100).

    Returns:
        A flat list of chunked Document objects, each carrying ``source``,
        ``page``, and ``chapter`` metadata keys.
    """
    chapter_map = build_chapter_map(documents)

    # Group documents by chapter in insertion order so chunks from the same
    # chapter are processed together.
    chapters: Dict[str, List[Document]] = {}
    for doc in documents:
        page_num = doc.metadata.get("page", 0)
        chapter = chapter_map.get(page_num, "Unknown Chapter")
        chapters.setdefault(chapter, []).append(doc)

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4o-mini",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: List[Document] = []
    for chapter_name, chapter_docs in chapters.items():
        chapter_chunks = splitter.split_documents(chapter_docs)
        for chunk in chapter_chunks:
            # Ensure chapter key is always present.
            chunk.metadata["chapter"] = chapter_name
            # Propagate source_name from the original document if present.
            if "source_name" not in chunk.metadata:
                for doc in chapter_docs:
                    if "source_name" in doc.metadata:
                        chunk.metadata["source_name"] = doc.metadata["source_name"]
                        break
        all_chunks.extend(chapter_chunks)

    return all_chunks
