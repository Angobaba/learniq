# Codebase Structure

**Analysis Date:** 2026-03-13

## Directory Layout

learniq/ contains:
- app/: Streamlit UI layer
- rag/: Core RAG pipeline
- scripts/: Executable scripts
- tests/: Unit test suite
- data/: Data storage (corpus, benchmarks, processed)
- docs/: Documentation
- chroma_db/: ChromaDB vector store (generated)
- .env: User environment variables
- .env.example: Template for .env
- requirements.txt: Python dependencies
- README.md: Project documentation

## Key File Locations

**Entry Points:**
- app/streamlit_app.py – Main app entry
- scripts/ingest_textbook.py – Ingestion entry
- scripts/run_app.sh – App launcher
- scripts/setup_and_run.sh – Combined setup script

**Core Logic:**
- rag/qa_chain.py – Answer generation
- rag/retriever.py – Vector search
- rag/vector_store.py – Persistence layer
- rag/chunker.py – Document chunking
- rag/loader.py – PDF loading
- rag/prompts.py – Prompt templates

**Testing:**
- tests/test_retrieval.py – Ingestion tests
- tests/test_citations.py – QA tests

## Naming Conventions

Files: snake_case.py for Python, UPPERCASE.md for docs
Directories: lowercase (app/, rag/, scripts/)
Functions: snake_case() for public, _snake_case() for private
Variables: snake_case, UPPERCASE for constants
Env vars: UPPERCASE_WITH_UNDERSCORES

## Where to Add New Code

New features go in corresponding layers:
- UI components: app/
- RAG components: rag/
- Executables: scripts/
- Tests: tests/
- Data: data/

Utilities should go in shared locations within their layer.

---

*Structure analysis: 2026-03-13*