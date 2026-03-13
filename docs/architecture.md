# LearnIQ – MVP Architecture

## Overview

LearnIQ is a Retrieval-Augmented Generation (RAG) application that lets CBSE Grade 8 Science students ask questions from their NCERT textbook and receive answers grounded strictly in the retrieved textbook content.

---

## High-Level Architecture

```
Student Question
      │
      ▼
┌─────────────────────────┐
│   Streamlit Chat UI      │
│   app/streamlit_app.py  │
└────────────┬────────────┘
             │ question
             ▼
┌─────────────────────────┐
│      Retriever           │
│   rag/retriever.py      │
│                         │
│  similarity_search(q)   │
│      top-k chunks       │
└────────────┬────────────┘
             │ top-k Document chunks
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────────────────┐
│ ChromaDB │  │  QA Chain             │
│ Vector   │  │  rag/qa_chain.py     │
│ Store    │  │                      │
│          │  │  prompt + context    │
│ chroma_db│  │  → GPT-4o-mini       │
└──────────┘  └──────────┬───────────┘
                         │ grounded answer + citations
                         ▼
              ┌─────────────────────────┐
              │   Streamlit Chat UI      │
              │   Display answer +       │
              │   source citations       │
              └─────────────────────────┘
```

---

## Component Descriptions

### `app/streamlit_app.py`
The main user interface. Provides:
- A chat input for student questions
- A response area displaying the grounded answer and source citations
- A sidebar showing app status and configuration
- Error handling for missing API key or missing vector store

### `rag/loader.py`
Uses LangChain's `PyPDFLoader` to load the NCERT PDF and return a list of `Document` objects (one per page), each with metadata including source path and page number.

### `rag/chunker.py`
Uses LangChain's `RecursiveCharacterTextSplitter` to split documents into smaller overlapping chunks (default 500 characters, 50 overlap). Smaller chunks improve retrieval precision.

### `rag/embeddings.py`
Creates an `OpenAIEmbeddings` instance using the `text-embedding-3-small` model. This model produces 1536-dimensional embeddings and is cost-effective.

### `rag/vector_store.py`
Wraps ChromaDB with two functions:
- `build_vector_store()` – embeds and persists a new store
- `load_vector_store()` – loads an existing store from disk

Persistence means ingestion only needs to happen once.

### `rag/retriever.py`
Performs cosine-similarity search in ChromaDB to return the top-k most relevant chunks for a given question.

### `rag/qa_chain.py`
Formats the retrieved chunks as a context block and constructs a prompt using the guardrailed template from `prompts.py`. Calls GPT-4o-mini via LangChain's `ChatOpenAI` to generate the answer. Extracts citation metadata from chunk metadata.

### `rag/prompts.py`
Defines the system prompt that enforces strict textbook grounding. See [prompt_guardrails.md](prompt_guardrails.md) for details.

---

## Data Flow

### Ingestion (one-time)

```
NCERT PDF
  └─→ loader.py (PyPDFLoader)
        └─→ chunker.py (RecursiveCharacterTextSplitter)
              └─→ embeddings.py (text-embedding-3-small)
                    └─→ vector_store.py (ChromaDB persist)
                          └─→ ./chroma_db/  (on disk)
```

### Query (real-time)

```
Student question
  └─→ embeddings.py (embed query)
        └─→ vector_store.py (similarity search)
              └─→ retriever.py (top-k chunks)
                    └─→ qa_chain.py (build prompt)
                          └─→ GPT-4o-mini (generate answer)
                                └─→ streamlit_app.py (display)
```

---

## Configuration

All runtime configuration is managed via environment variables (`.env`):

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Authentication for OpenAI |
| `MODEL_NAME` | LLM (default: gpt-4o-mini) |
| `EMBEDDING_MODEL` | Embedding model (default: text-embedding-3-small) |
| `CHROMA_PERSIST_DIR` | ChromaDB storage directory |
| `TEXTBOOK_PATH` | Path to the NCERT PDF |
| `TOP_K` | Number of chunks to retrieve |
| `CHUNK_SIZE` | Characters per chunk |
| `CHUNK_OVERLAP` | Overlap between consecutive chunks |

---

## Design Decisions

| Decision | Rationale |
|---|---|
| ChromaDB persistence | Avoids re-embedding on every app restart (cost + latency) |
| RecursiveCharacterTextSplitter | Tries to split on paragraph/sentence boundaries first |
| text-embedding-3-small | Good quality, low cost, 1536 dimensions |
| GPT-4o-mini | Balanced cost/quality for educational Q&A |
| temperature=0 | Deterministic, factual answers – no creative hallucination |
| Strict grounding prompt | Prevents the model from using outside knowledge |

---

## Future Enhancements (out of MVP scope)

- Adaptive quiz generation
- Teacher dashboard with usage analytics
- Bilingual support (Hindi / English)
- Voice interface
- Semantic similarity scoring for benchmark evaluation (e.g., RAGAS)
- Fine-tuning on CBSE curriculum questions
