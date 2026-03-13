# Technology Stack

**Analysis Date:** 2026-03-13

## Languages

**Primary:**
- Python 3.14.3 - Backend RAG pipeline, Streamlit web app, and ingestion scripts

**Secondary:**
- Shell scripting (Bash) - Setup and execution scripts

## Runtime

**Environment:**
- Python 3.14.3

**Package Manager:**
- pip
- Lockfile: `requirements.txt` (present)

## Frameworks

**Core:**
- Streamlit 1.32.0+ - Web UI for chat interface (`app/streamlit_app.py`)
- LangChain 0.2.0+ - Orchestration for RAG pipeline, document loaders, text splitters
- LangChain-OpenAI 0.1.0+ - OpenAI integration (ChatOpenAI, OpenAIEmbeddings)
- LangChain-Chroma 0.1.0+ - Vector store integration with Chroma

**Data Processing:**
- PyPDF 4.2.0+ - PDF loading and parsing (`rag/loader.py`)
- LangChain-Text-Splitters 0.2.0+ - Document chunking with RecursiveCharacterTextSplitter (`rag/chunker.py`)
- ChromaDB 0.5.0+ - Vector store for embeddings persistence

**AI/ML:**
- OpenAI API client 1.25.0+ - Direct API calls for LLM and embeddings
- tiktoken 0.7.0+ - Token counting for OpenAI models

**Testing:**
- pytest 8.0.0+ - Test framework (configuration: default, runner: `tests/`)

**Environment Management:**
- python-dotenv 1.0.0+ - Environment variable loading from `.env` file

## Key Dependencies

**Critical:**
- langchain (0.2.0+) - Core RAG orchestration and document handling
- langchain-openai (0.1.0+) - Bridge between LangChain and OpenAI services
- openai (1.25.0+) - Direct OpenAI API calls (fallback/direct usage)
- chromadb (0.5.0+) - Persistent vector storage; required for every app start
- streamlit (1.32.0+) - Web frontend; required for UI interaction

**Infrastructure:**
- python-dotenv (1.0.0+) - Configuration loading; essential for API key and textbook path management
- pypdf (4.2.0+) - PDF parsing; required for ingestion pipeline
- tiktoken (0.7.0+) - Token counting for embeddings and LLM inputs

## Configuration

**Environment:**
- Configuration via `.env` file (template: `.env.example`)
- Required environment variables:
  - `OPENAI_API_KEY` - OpenAI API authentication (no default)
  - `MODEL_NAME` - LLM model (default: `gpt-4o-mini`)
  - `EMBEDDING_MODEL` - Embedding model (default: `text-embedding-3-small`)
  - `CHROMA_PERSIST_DIR` - Vector store location (default: `./chroma_db`)
  - `TEXTBOOK_PATH` - Path to NCERT PDF (default: `./data/raw/NCERT_Class8_Science.pdf`)
  - `TOP_K` - Number of chunks to retrieve (default: `4`)
  - `CHUNK_SIZE` - Characters per chunk (default: `500`)
  - `CHUNK_OVERLAP` - Overlap between chunks (default: `50`)

**Build:**
- No build configuration files (Streamlit runs directly)
- No TypeScript, no transpilation needed

## Platform Requirements

**Development:**
- Python 3.14.3 or compatible
- pip for package management
- Terminal/shell for running scripts (Bash on Unix/macOS/Git Bash, cmd on Windows)
- OpenAI API key with access to `gpt-4o-mini` and `text-embedding-3-small` models

**Production:**
- Python 3.14.3 or compatible
- pip dependencies installed
- OpenAI API key for LLM and embeddings access
- Minimum disk space: ~500MB for ChromaDB vector store (varies with textbook size)
- Streamlit web framework (no separate server needed; Streamlit serves the app)

---

*Stack analysis: 2026-03-13*
