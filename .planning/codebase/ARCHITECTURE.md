# Architecture

**Analysis Date:** 2026-03-13

## Pattern Overview

**Overall:** Retrieval-Augmented Generation (RAG) with strict grounding

**Key Characteristics:**
- Textbook content is ingested once, stored persistently in ChromaDB
- Student questions trigger a two-stage pipeline: (1) semantic retrieval, (2) grounded LLM response generation
- All answers are constrained to retrieved chunks only—no outside knowledge allowed
- Citations are automatically extracted from chunk metadata for transparency
- Stateless query pipeline enables scalability

## Layers

**Data Ingestion Layer:**
- Purpose: Convert PDF textbook into embeddings and persist in vector database
- Location: `scripts/ingest_textbook.py`, `rag/loader.py`, `rag/chunker.py`, `rag/embeddings.py`, `rag/vector_store.py`
- Contains: PDF loading, document chunking, embedding generation, ChromaDB persistence
- Depends on: OpenAI embeddings API, ChromaDB
- Used by: One-time setup; called before app can run
- Entry: `scripts/ingest_textbook.py` main() orchestrates the full ingestion workflow

**Retrieval Layer:**
- Purpose: Find semantically similar textbook content for a given question
- Location: `rag/retriever.py`, `rag/vector_store.py`
- Contains: Vector similarity search against ChromaDB
- Depends on: Embedded chunks in ChromaDB, embeddings model to encode queries
- Used by: QA Layer
- Key function: `retrieve_chunks(vector_store, query, top_k)` returns top-k Document objects

**QA Layer:**
- Purpose: Generate grounded answers using retrieved context and LLM
- Location: `rag/qa_chain.py`, `rag/prompts.py`
- Contains: Prompt construction, LLM invocation, citation extraction
- Depends on: Retrieval Layer output (chunks), OpenAI LLM API, prompt templates
- Used by: UI Layer
- Key functions:
  - `answer_question(question, chunks, llm)` - main entry point
  - `_format_context(chunks)` - formats retrieved chunks with citations
  - `_extract_citations(chunks)` - deduplicates source metadata

**UI Layer:**
- Purpose: Provide conversational chat interface for students
- Location: `app/streamlit_app.py`
- Contains: Chat input, session state management, response display, error handling
- Depends on: All lower layers (loader on demand, retriever, QA chain)
- Used by: Student users via Streamlit web interface

## Data Flow

**Ingestion Flow (one-time, after PDF is placed):**

1. `scripts/ingest_textbook.py` main() validates environment (checks for OPENAI_API_KEY)
2. Calls `rag.loader.load_pdf(textbook_path)` returns List[Document] (one per PDF page)
3. Calls `rag.chunker.chunk_documents(documents, chunk_size=500, chunk_overlap=50)` returns List[Document] chunks
4. Calls `rag.embeddings.get_embeddings()` returns OpenAIEmbeddings instance
5. Calls `rag.vector_store.build_vector_store(chunks, persist_dir)` embeds and persists to ./chroma_db/
6. Workflow prints success and confirms app can run

**Query Flow (real-time, per student question):**

1. `app/streamlit_app.py` receives question from chat input
2. Validates prerequisites: OPENAI_API_KEY set, vector store exists
3. Calls `rag.vector_store.load_vector_store()` returns loaded Chroma instance
4. Calls `rag.retriever.retrieve_chunks()` performs cosine-similarity search
5. Calls `rag.qa_chain.build_qa_chain()` returns ChatOpenAI instance (temperature=0)
6. Calls `rag.qa_chain.answer_question(question, chunks, llm)` with context formatting and citation extraction
7. `streamlit_app.py` displays answer and citations

**State Management:**

- Session State: Streamlit maintains chat history during user session
- Persistent State: ChromaDB persists on disk between app restarts
- Stateless Query: Each question is independent

## Key Abstractions

**Document:**
- Purpose: Chunk of text with metadata (source file, page number)
- Pattern: LangChain Document class with metadata dict

**Vector Store:**
- Purpose: Abstraction over ChromaDB
- Location: `rag/vector_store.py`
- Pattern: Wraps LangChain Chroma; collection name fixed to learniq_textbook

**Retriever:**
- Purpose: Encapsulates similarity search
- Location: `rag/retriever.py`
- Pattern: Configurable top_k from env (default 4)

**QA Chain:**
- Purpose: Orchestrates prompt, LLM, response flow
- Location: `rag/qa_chain.py`
- Pattern: Returns dict with answer, citations, found keys

## Entry Points

**Ingestion:**
- Location: `scripts/ingest_textbook.py`
- Triggers: Manual run once per PDF change
- Responsibilities: Validate environment, load PDF, chunk, embed, persist

**App:**
- Location: `app/streamlit_app.py`
- Triggers: User starts app via streamlit run command
- Responsibilities: UI, session state, retrieval orchestration

## Error Handling

**Strategy:** Graceful degradation with clear user messaging

- Missing API Key: Validation at module load and app start
- Missing Vector Store: Check before operations
- PDF File Not Found: FileNotFoundError with helpful message
- LLM Failures: Try/except with user-facing error display
- Empty Results: Return special no-context response

## Cross-Cutting Concerns

**Logging:** No structured logging in MVP. Uses print() and Streamlit UI.
**Validation:** Environment checks, file existence checks, simple input validation.
**Authentication:** OpenAI API key via .env environment variable.
**Configuration:** All config via environment variables with sensible defaults.

---

*Architecture analysis: 2026-03-13*