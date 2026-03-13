# External Integrations

**Analysis Date:** 2026-03-13

## APIs & External Services

**OpenAI:**
- LLM API (Chat Completions) - Used for answering student questions based on retrieved context
  - SDK/Client: `langchain-openai` / `openai` package
  - Auth: `OPENAI_API_KEY` environment variable
  - Models used:
    - `gpt-4o-mini` (default) - QA generation in `rag/qa_chain.py`
    - Configurable via `MODEL_NAME` env var
- Embeddings API - Used for encoding textbook chunks and student queries
  - SDK/Client: `langchain-openai.OpenAIEmbeddings`
  - Auth: `OPENAI_API_KEY` environment variable
  - Model used: `text-embedding-3-small` (default)
  - Configurable via `EMBEDDING_MODEL` env var
  - Used in `rag/embeddings.py`

## Data Storage

**Databases:**
- ChromaDB (vector database)
  - Purpose: Persistent storage of embedded textbook chunks
  - Connection: Local file-based persistence via `CHROMA_PERSIST_DIR` env var (default: `./chroma_db`)
  - Client: `langchain-chroma.Chroma`
  - Location: `rag/vector_store.py` - `build_vector_store()` and `load_vector_store()` functions
  - Collection name: `learniq_textbook`
  - No remote database; all data stored locally on disk
  - Persists embeddings, chunk content, and metadata (source, page number)

**File Storage:**
- Local filesystem only
  - Textbook PDF: `./data/raw/NCERT_Class8_Science.pdf` (configurable via `TEXTBOOK_PATH`)
  - Processed chunks: Persisted in ChromaDB local store
  - No cloud storage integration (S3, GCS, etc.)

**Caching:**
- None - Real-time embeddings on each query

## Authentication & Identity

**Auth Provider:**
- Custom / API key-based
- Implementation: Direct environment variable-based API key (`OPENAI_API_KEY`)
- No user authentication system in Phase 1 MVP
- No session management or user tracking
- Streamlit's built-in session state for conversation history (in-memory per browser session)

## Monitoring & Observability

**Error Tracking:**
- None detected - No Sentry, Rollbar, or similar integration

**Logs:**
- Console logging via Python `print()` statements
- No centralized logging service
- Logs in:
  - `app/streamlit_app.py` - Status indicators and error messages displayed in Streamlit UI
  - `scripts/ingest_textbook.py` - Progress updates to stdout during ingestion
  - `tests/benchmark_runner.py` - Test results to stdout

## CI/CD & Deployment

**Hosting:**
- Local development only (Phase 1 MVP)
- Streamlit web framework; can be deployed to Streamlit Cloud, Heroku, or any Python hosting platform
- No current cloud deployment (works on user's machine)

**CI Pipeline:**
- None - No GitHub Actions, GitLab CI, or other CI/CD configured

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY` - OpenAI API key (no default; required for operation)
- `MODEL_NAME` - LLM model name (default: `gpt-4o-mini`)
- `EMBEDDING_MODEL` - Embedding model name (default: `text-embedding-3-small`)
- `CHROMA_PERSIST_DIR` - Vector store directory (default: `./chroma_db`)
- `TEXTBOOK_PATH` - Path to PDF file (default: `./data/raw/NCERT_Class8_Science.pdf`)
- `TOP_K` - Number of chunks to retrieve (default: `4`)
- `CHUNK_SIZE` - Characters per chunk (default: `500`)
- `CHUNK_OVERLAP` - Overlap between chunks (default: `50`)

**Secrets location:**
- `.env` file (local, not committed)
- Template: `.env.example` (contains non-secret defaults)
- Loading: `python-dotenv` in both `app/streamlit_app.py` and `scripts/ingest_textbook.py`

## Webhooks & Callbacks

**Incoming:**
- None - No webhook endpoints

**Outgoing:**
- None - No outbound webhooks or callbacks to external services

## Data Flow & Integration Patterns

**Textbook Ingestion Flow:**
1. `scripts/ingest_textbook.py` - Entry point for one-time data preparation
2. Loads PDF from `TEXTBOOK_PATH` via `rag/loader.py` (uses PyPDFLoader)
3. Chunks documents in `rag/chunker.py` (uses RecursiveCharacterTextSplitter)
4. Embeds chunks in `rag/embeddings.py` (calls OpenAI Embeddings API)
5. Stores in ChromaDB via `rag/vector_store.py` (persists to `CHROMA_PERSIST_DIR`)

**Question-Answering Flow:**
1. `app/streamlit_app.py` - User enters question in chat interface
2. `rag/retriever.py` - Retrieves top-k similar chunks from ChromaDB
3. `rag/qa_chain.py` - Calls OpenAI LLM with retrieved context and system prompt
4. System prompt in `rag/prompts.py` - Enforces textbook-grounding and source citations
5. Response returned to Streamlit UI with citations

**Benchmark Evaluation Flow:**
1. `tests/benchmark_runner.py` - Loads benchmark JSON from `data/benchmarks/`
2. For each benchmark question, runs full QA pipeline
3. Evaluates answers against expected keywords
4. Reports pass/fail and overall accuracy to stdout

---

*Integration audit: 2026-03-13*
