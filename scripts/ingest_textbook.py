#!/usr/bin/env python3
"""
ingest_textbook.py – Load the NCERT Grade 8 Science PDF, chunk it, embed it,
and persist a ChromaDB vector store for use by the LearnIQ app.

Usage:
    python scripts/ingest_textbook.py

Environment variables (set in .env):
    TEXTBOOK_PATH       Path to the PDF file
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

from rag.loader import load_pdf
from rag.chunker import chunk_documents
from rag.vector_store import build_vector_store


def main() -> None:
    print("=" * 60)
    print("LearnIQ – Textbook Ingestion")
    print("=" * 60)

    # Validate environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "\n[ERROR] OPENAI_API_KEY is not set.\n"
            "Copy .env.example to .env and fill in your API key, then re-run."
        )
        sys.exit(1)

    textbook_path = os.getenv("TEXTBOOK_PATH", "./data/raw/NCERT_Class8_Science.pdf")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    print(f"\nTextbook path : {textbook_path}")
    print(f"ChromaDB dir  : {chroma_dir}")

    # Step 1 – Delete old vector store to prevent stale 500-char chunks mixing
    # with new 800-token chapter-aware chunks.
    print("\n[1/4] Checking for existing vector store…")
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

    # Step 2 – Load PDF
    print("\n[2/4] Loading PDF…")
    t0 = time.time()
    try:
        documents = load_pdf(textbook_path)
    except FileNotFoundError as exc:
        print(f"\n[ERROR] {exc}")
        sys.exit(1)
    print(f"      Loaded {len(documents)} page(s) in {time.time() - t0:.1f}s")

    # Step 3 – Chunk (chapter-aware, token-based 800/100)
    print("\n[3/4] Chunking documents…")
    t0 = time.time()
    chunks = chunk_documents(documents)
    print(f"      Created {len(chunks)} chunk(s) in {time.time() - t0:.1f}s")

    # Validate chapter metadata
    chapters_found = set(c.metadata.get("chapter", "?") for c in chunks)
    print(f"      Chapters detected: {len(chapters_found)}")
    for ch in sorted(chapters_found):
        print(f"        - {ch}")

    # Step 4 – Embed & persist
    print("\n[4/4] Embedding and persisting to ChromaDB…")
    print("      This may take a few minutes depending on document size.")
    t0 = time.time()
    build_vector_store(chunks, persist_dir=chroma_dir)
    print(f"      Done in {time.time() - t0:.1f}s")

    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print(f"Vector store saved to: {chroma_dir}")
    print("You can now run the app with: streamlit run app/streamlit_app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
