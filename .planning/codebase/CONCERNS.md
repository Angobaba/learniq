# Codebase Concerns

**Analysis Date:** 2026-03-13

## Tech Debt

### Broad Exception Handling in Production UI
- Issue: `app/streamlit_app.py` line 163 catches all exceptions with bare `except Exception` and displays raw error messages to users
- Files: `app/streamlit_app.py` (line 163-168)
- Impact: Users see potentially sensitive error details (API failures, stack traces). Difficult to debug production issues. Poor user experience.
- Fix approach: Implement structured error handling that categorizes exceptions (network, API, validation, etc.) and shows user-friendly messages while logging full details server-side for debugging

### Duplicate API Key Validation Logic
- Issue: API key validation is repeated in three places with identical error messages
- Files: `rag/embeddings.py` (line 25-30), `rag/qa_chain.py` (line 52-57), `scripts/ingest_textbook.py` (line 40-46)
- Impact: Makes it harder to maintain consistent messaging and update validation logic. Code duplication violates DRY principle.
- Fix approach: Extract validation to a shared utility function in `rag/` (e.g., `rag/config.py` or `rag/validation.py`) that both modules and scripts import

### ChromaDB Rebuild on Every Ingest
- Issue: `rag/vector_store.py` line 22 notes "If a store already exists at *persist_dir* it will be overwritten"
- Files: `rag/vector_store.py` (line 16-42)
- Impact: Running ingestion script twice will lose any metadata, rebuild time is wasted, vector store changes are not incremental. Unsafe for production.
- Fix approach: Add a flag to `build_vector_store()` to allow append vs. overwrite modes. Check for existing store before rebuilding.

### No Logging Infrastructure
- Issue: Codebase uses only print statements and exception messages; no structured logging
- Files: All Python files, especially `app/streamlit_app.py`, `scripts/ingest_textbook.py`, `tests/benchmark_runner.py`
- Impact: Production debugging is difficult. No audit trail of user queries or system events. Hard to monitor and alert on issues.
- Fix approach: Integrate Python's `logging` module or structured logging library (e.g., structlog). Add debug-level logs to retrieval pipeline and LLM calls.

## Known Bugs

### Unreliable Citation Page Extraction
- Symptoms: Some PDFs may return `"page": "?"` when page metadata is missing from chunks
- Files: `rag/qa_chain.py` (line 20, 31), `app/streamlit_app.py` (line 149-150)
- Trigger: PDFs where PyPDF2 fails to extract page numbers correctly (varies by PDF structure)
- Workaround: None. UI displays "Page ?" which is confusing. Consider tracking source chunk ID instead of page number.

### Response Formatting Duplication
- Symptoms: Answer formatting and citation append logic is duplicated between display and session storage
- Files: `app/streamlit_app.py` (line 142-157)
- Trigger: Every user query processes citations twice (once for display, once for session state)
- Workaround: None internally; only affects performance marginally
- Fix approach: Refactor to a single format function that returns formatted answer and citations in one structure

## Security Considerations

### API Key Passed to LLM Constructor
- Risk: API keys are passed as string arguments to `ChatOpenAI()` and `OpenAIEmbeddings()` instead of relying solely on environment variables
- Files: `rag/qa_chain.py` (line 62), `rag/embeddings.py` (line 35)
- Current mitigation: API key is read from environment variable in both cases, not hardcoded
- Recommendations:
  - Use LangChain's built-in environment variable handling by NOT passing `openai_api_key=api_key` explicitly
  - LangChain should read from `OPENAI_API_KEY` automatically; passing it as a parameter is unnecessary and increases exposure surface
  - Remove explicit API key passing to reduce chance of accidental logging or exposure

### No Rate Limiting or Request Throttling
- Risk: Nothing prevents users from hammering the app with queries, causing high OpenAI API costs
- Files: `app/streamlit_app.py` (no throttling logic), `rag/retriever.py` (no rate limiting)
- Current mitigation: None
- Recommendations:
  - Add per-session or per-user query rate limits (e.g., max 10 queries per minute)
  - Implement exponential backoff for API failures
  - Add cost monitoring and alerting

### Lack of Input Validation
- Risk: User questions are passed directly to embeddings and LLM without sanitization
- Files: `app/streamlit_app.py` (line 104, 136), `rag/retriever.py` (line 32-50)
- Current mitigation: LLM prompt guards against using outside knowledge, but injection attacks (e.g., prompt manipulation) are possible
- Recommendations:
  - Validate question length (max 1000 chars)
  - Strip suspicious characters/control sequences
  - Log suspicious queries for manual review

## Performance Bottlenecks

### Embeddings Generated on Every App Initialization
- Problem: `load_vector_store()` calls `get_embeddings()` which creates a new OpenAIEmbeddings instance every time the vector store is loaded
- Files: `rag/vector_store.py` (line 68), `app/streamlit_app.py` (line 133)
- Cause: Embedding object is not cached; LangChain may perform API calls to validate the model on init
- Improvement path:
  - Cache embedding instance in a module-level variable or in Streamlit session state
  - Consider lazy initialization only when embeddings are actually used for similarity search

### Vector Store Reload on Every Query
- Problem: `app/streamlit_app.py` line 133 loads the entire vector store from disk on each user query
- Files: `app/streamlit_app.py` (line 133)
- Cause: No persistence of vector store object across chat turns; full initialization from ChromaDB files
- Improvement path:
  - Store vector store in Streamlit session state to persist across turns
  - Profile to determine actual impact (may be acceptable depending on vector store size)

### Benchmark Keyword Matching Too Simplistic
- Problem: `tests/benchmark_runner.py` line 81 uses naive substring matching (`if kw in answer_lower`)
- Files: `tests/benchmark_runner.py` (line 81)
- Cause: Case-insensitive substring matching catches false positives (e.g., "are" matches "care", "tree")
- Improvement path:
  - Use regex word boundaries or tokenization for exact word matching
  - Implement semantic similarity scoring (e.g., RAGAS framework, embedding-based matching)

## Fragile Areas

### Monolithic Streamlit App
- Files: `app/streamlit_app.py` (168 lines)
- Why fragile: Single file handles configuration, UI rendering, error handling, and orchestration. Any change to one layer affects the whole app. Hard to test individual components.
- Safe modification: Extract into layers: `config.py` (env/sidebar logic), `ui.py` (chat UI), `handlers.py` (question handling)
- Test coverage: Streamlit apps are notoriously hard to unit test. Current codebase has no tests for the UI layer. Only indirect tests via benchmark runner.

### Tight Coupling Between Retrieval and QA
- Files: `app/streamlit_app.py` line 134-136, `rag/qa_chain.py`, `rag/retriever.py`
- Why fragile: App logic directly calls `retrieve_chunks()` then `answer_question()`. If either changes signature or behavior, app breaks. No abstraction.
- Safe modification: Create a `RAGPipeline` class or module that encapsulates the full retrieval + QA flow, exposing a single `query()` method
- Test coverage: Limited to unit tests of individual functions. No integration tests for the full pipeline.

### Chunk Metadata Assumptions
- Files: `app/streamlit_app.py` (line 148-150), `rag/qa_chain.py` (line 20, 31), `tests/test_citations.py`
- Why fragile: Code assumes all chunks have `source` and `page` metadata. If ChromaDB is rebuilt with different metadata schema, citations break silently.
- Safe modification: Add metadata schema validation when loading vector store. Raise clear errors if expected fields are missing.
- Test coverage: Basic tests exist (test_citations.py) but don't cover schema migration or missing metadata scenarios.

### Hard-Coded Defaults Scattered Throughout
- Files: `app/streamlit_app.py` (line 47-48), `rag/chunker.py` (line 34-36), `rag/retriever.py` (line 24), `rag/vector_store.py` (line 33, 59), `rag/embeddings.py` (line 33), `scripts/ingest_textbook.py` (line 48-49)
- Why fragile: Default values (TOP_K=4, CHUNK_SIZE=500, etc.) are defined in multiple places. Changing defaults requires editing multiple files.
- Safe modification: Centralize all defaults in a single config module (`rag/config.py`) that all modules import
- Test coverage: No tests for default values; if defaults change, tests don't catch it.

## Scaling Limits

### Single-PDF-Only Architecture
- Current capacity: NCERT Grade 8 Science textbook only
- Limit: Cannot add Hindi textbook, past papers, or other curriculum materials without re-architecting ingestion
- Files: `scripts/ingest_textbook.py` (single PDF input), `rag/vector_store.py` (single collection)
- Scaling path:
  - Modify ingestion to support multiple PDFs in a batch
  - Create separate collections or namespaces per curriculum/language
  - Implement collection switching logic in retriever

### Vector Store Size Growth
- Current capacity: NCERT Grade 8 Science (estimated ~300-400 pages = ~1000-2000 chunks at CHUNK_SIZE=500)
- Limit: ChromaDB performance degrades as collections grow beyond 1M vectors. Retrieval latency increases.
- Files: `rag/vector_store.py`, `rag/retriever.py` (similarity_search with k=4)
- Scaling path:
  - Implement hierarchical retrieval (e.g., chapter-level filtering before semantic search)
  - Use metadata filtering in Chroma to narrow search space
  - Profile retrieval latency as corpus grows; consider pagination or caching strategies

### Session State Memory
- Current capacity: Streamlit session state stores all chat history in memory
- Limit: If user asks 100+ questions, memory usage grows linearly. Long sessions may crash on memory-constrained systems.
- Files: `app/streamlit_app.py` (line 92-93, 159)
- Scaling path:
  - Implement message pruning (keep only last N messages) or archival to disk
  - Use Streamlit's cache or a lightweight local database for chat history

## Dependencies at Risk

### Fixed LangChain Dependencies Without Pinning Patch Versions
- Risk: `requirements.txt` specifies `langchain>=0.2.0` and `langchain-*>=0.x.y` without upper bounds. Minor version bumps could break compatibility (LangChain has rapid iteration).
- Impact: Running `pip install -r requirements.txt` on different dates installs different versions, causing non-reproducible environments
- Files: `requirements.txt` (lines 2-7)
- Migration plan:
  - Generate a `requirements-lock.txt` or `Pipfile.lock` with pinned versions
  - Use `pip freeze > requirements-lock.txt` after successful testing
  - Maintain `requirements.txt` for development flexibility; use lock file for production

### Deprecated PyPDF Library
- Risk: Project uses `pypdf>=4.2.0`. PyPDF has known issues with complex PDF structures and inconsistent page extraction.
- Impact: Citations may fail for some PDFs. Page numbers may be incorrect or missing.
- Files: `requirements.txt` (line 10), `rag/loader.py` (uses PyPDFLoader)
- Migration plan:
  - Evaluate `pypdf` vs. `pdfplumber` (better OCR, more reliable page extraction)
  - Test both on NCERT PDF and other education materials
  - Switch if reliability improves, but requires re-ingestion

### OpenAI API Dependency
- Risk: Entire system is tightly coupled to OpenAI (embeddings and LLM). Price increases or API deprecations directly impact product
- Impact: Cannot easily switch to open-source models (Llama, Mistral) or other providers (Anthropic, Azure) without major refactoring
- Files: `rag/embeddings.py`, `rag/qa_chain.py` (hardcoded OpenAI)
- Migration plan:
  - Introduce an abstraction layer for LLM and embedding providers (e.g., Enum or Strategy pattern)
  - Allow configuration of provider and model via environment variables
  - Test with alternative providers in Phase 2

## Missing Critical Features

### No Output Validation or Hallucination Detection
- Problem: System generates answers but has no built-in check for whether answers actually match the retrieved context
- Blocks: Cannot reliably detect when the LLM ignored the prompt guardrails and used outside knowledge
- Files: `rag/qa_chain.py` (no validation of output), `rag/prompts.py` (guardrails only in prompt, not enforced)
- Recommended fix:
  - Implement semantic similarity check between answer and retrieved chunks
  - Flag answers with low semantic similarity for manual review
  - Add a re-ranking step using embedding distance

### No Citation Verification
- Problem: Citations are extracted from metadata but never verified to match the answer text
- Blocks: Users cannot trust that cited pages actually contain the cited concepts
- Files: `rag/qa_chain.py` (lines 25-36 extract citations but don't validate)
- Recommended fix:
  - For each citation, compute similarity between answer text and chunk text
  - Warn if similarity is below threshold
  - Re-rank or filter citations based on relevance

### No Multi-Turn Query Understanding
- Problem: Each question is treated independently. No context or history is used to improve retrieval
- Blocks: Follow-up questions like "Why does that happen?" fail because system doesn't remember prior context
- Files: `app/streamlit_app.py` (stores chat history but doesn't use it for retrieval)
- Recommended fix:
  - Implement query rewriting using chat history to expand follow-up questions
  - Add a lightweight memory layer that tracks key entities/topics from prior turns
  - Concatenate expanded query + history context to retriever

### No Fallback for Out-of-Context Responses
- Problem: If retriever returns empty results, system shows hardcoded fallback. No graceful degradation or retry logic.
- Blocks: Cannot suggest "Did you mean?" or alternative questions
- Files: `rag/qa_chain.py` (line 84-89), `rag/prompts.py` (hardcoded NO_CONTEXT_RESPONSE)
- Recommended fix:
  - Implement query expansion (e.g., synonyms, variations) and retry with modified query
  - Suggest related topics the system CAN answer
  - Track unanswerable questions for curriculum gap analysis

## Test Coverage Gaps

### No Tests for Streamlit UI
- What's not tested: Chat message rendering, error display, sidebar configuration, API key validation in UI
- Files: `app/streamlit_app.py` (entire file)
- Risk: Changes to UI layout or logic could break user experience without being caught
- Coverage: 0%; only indirect tests via manual benchmark runner and user testing

### No Integration Tests
- What's not tested: Full pipeline from PDF ingestion through chat response
- Files: No integration test file exists
- Risk: Unit tests pass but components fail when integrated (e.g., metadata format mismatch between ingestion and retrieval)
- Coverage: 0%

### No End-to-End Tests
- What's not tested: Real scenario: user asks question → system retrieves and answers
- Files: No E2E test file; benchmark runner is closest but manual, not automated
- Risk: Deployment to production could fail unexpectedly
- Coverage: Manual only (human runs benchmark_runner.py)

### Incomplete Unit Test Coverage
- What's not tested:
  - `rag/vector_store.py` (no tests for build_vector_store or load_vector_store)
  - `app/streamlit_app.py` (no tests, Streamlit apps are hard to test)
  - `rag/prompts.py` (no tests, just constants)
  - `scripts/ingest_textbook.py` (no unit tests, only manual testing)
  - Error handling paths in various modules
- Files: Test files exist but sparse coverage
- Risk: Bugs in vector store initialization, PDF loading, or prompt formatting could go undetected
- Coverage: Estimated ~30-40%; high-risk areas (retrieval, citations) have some tests but critical paths (UI, ingestion) do not

### No Performance / Regression Tests
- What's not tested: Retrieval latency, embedding API costs, chunking time
- Files: No perf test file
- Risk: Performance regressions go unnoticed until production (e.g., TOP_K tuning slows down queries 10x)
- Coverage: 0%; only benchmark_runner.py checks correctness, not speed

---

*Concerns audit: 2026-03-13*
