#!/usr/bin/env python3
"""
ingest_textbook.py – Load Grade 8 Science PDFs, chunk them, embed them,
and persist a ChromaDB vector store for use by the LearnIQ app.

Supports two modes:
  1. Single PDF via TEXTBOOK_PATH (backward compatible)
  2. Directory scan via SOURCES_DIR (loads all PDFs recursively)

If SOURCES_DIR is set and exists, it takes precedence over TEXTBOOK_PATH.

Usage:
    python scripts/ingest_textbook.py

Environment variables (set in .env):
    SOURCES_DIR         Directory containing PDF source files (recommended)
    TEXTBOOK_PATH       Path to a single PDF file (fallback)
    CHROMA_PERSIST_DIR  Directory for ChromaDB persistence
    OPENAI_API_KEY      Your OpenAI API key
    EMBEDDING_MODEL     Embedding model name  (default: text-embedding-3-small)
"""

import io
import os
import shutil
import sys
import time

# Ensure stdout handles UTF-8 on Windows (avoids UnicodeEncodeError for chapter names)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

# Allow imports from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from rag.loader import load_pdf, load_sources_dir
from rag.chunker import chunk_documents
from rag.vector_store import build_vector_store


def main() -> None:
    print("=" * 60)
    print("LearnIQ – Source Ingestion")
    print("=" * 60)

    # Validate environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "\n[ERROR] OPENAI_API_KEY is not set.\n"
            "Copy .env.example to .env and fill in your API key, then re-run."
        )
        sys.exit(1)

    sources_dir = os.getenv("SOURCES_DIR", "./data/raw")
    textbook_path = os.getenv("TEXTBOOK_PATH", "./data/raw/NCERT_Class8_Science.pdf")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Determine loading mode
    use_dir = os.path.isdir(sources_dir)

    if use_dir:
        print(f"\nSources dir   : {sources_dir} (scanning for all PDFs)")
    else:
        print(f"\nTextbook path : {textbook_path} (single file mode)")
    print(f"ChromaDB dir  : {chroma_dir}")

    # Step 1 – Delete old vector store
    print("\n[1/4] Checking for existing vector store...")
    if os.path.exists(chroma_dir):
        print(f"      Removing existing vector store at {chroma_dir}...")
        try:
            shutil.rmtree(chroma_dir)
            print("      Old vector store deleted.")
        except PermissionError as exc:
            print(
                f"\n[ERROR] Cannot delete {chroma_dir} — files are locked by another process.\n"
                "        Close any running instances of the app (Streamlit, Python) that may\n"
                "        have the ChromaDB open, then re-run this script.\n"
                f"        Details: {exc}"
            )
            sys.exit(1)
    else:
        print("      No existing vector store found, starting fresh.")

    # Step 2 – Load PDFs
    print("\n[2/4] Loading source documents...")
    t0 = time.time()
    try:
        if use_dir:
            documents = load_sources_dir(sources_dir)
        else:
            documents = load_pdf(textbook_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"\n[ERROR] {exc}")
        sys.exit(1)

    # Show what was loaded
    source_names = set(d.metadata.get("source_name", "Unknown") for d in documents)
    print(f"      Loaded {len(documents)} page(s) from {len(source_names)} source(s) in {time.time() - t0:.1f}s")
    for name in sorted(source_names):
        count = sum(1 for d in documents if d.metadata.get("source_name") == name)
        print(f"        - {name} ({count} pages)")

    # Step 3 – Chunk (chapter-aware, token-based 800/100)
    print("\n[3/4] Chunking documents...")
    t0 = time.time()
    chunks = chunk_documents(documents)
    print(f"      Created {len(chunks)} chunk(s) in {time.time() - t0:.1f}s")

    # Validate chapter metadata
    chapters_found = set(c.metadata.get("chapter", "?") for c in chunks)
    print(f"      Chapters detected: {len(chapters_found)}")
    for ch in sorted(chapters_found):
        print(f"        - {ch}")

    # Validate source metadata
    sources_in_chunks = set(c.metadata.get("source_name", "?") for c in chunks)
    print(f"      Sources in chunks: {len(sources_in_chunks)}")
    for src in sorted(sources_in_chunks):
        count = sum(1 for c in chunks if c.metadata.get("source_name") == src)
        print(f"        - {src} ({count} chunks)")

    # Step 4 – Embed & persist
    print("\n[4/4] Embedding and persisting to ChromaDB...")
    print("      This may take a few minutes depending on document size.")
    t0 = time.time()
    build_vector_store(chunks, persist_dir=chroma_dir)
    print(f"      Done in {time.time() - t0:.1f}s")

    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print(f"Sources ingested: {len(source_names)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Vector store saved to: {chroma_dir}")
    print("You can now run the app with: streamlit run app/streamlit_app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
