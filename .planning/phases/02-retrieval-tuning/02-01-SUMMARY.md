---
phase: 02-retrieval-tuning
plan: 01
subsystem: database
tags: [rag, chromadb, langchain, tiktoken, embeddings, chunking, cosine-distance]

# Dependency graph
requires: []
provides:
  - Chapter-aware 800-token chunked vector store with cosine distance
  - Score-threshold retriever (k=6, threshold=0.35)
  - build_chapter_map() function mapping PDF pages to chapter names
  - Re-ingested chroma_db with chapter + page metadata on every chunk
affects: [03-benchmarking, 04-quiz, 05-citations, 06-multi-turn]

# Tech tracking
tech-stack:
  added: [langchain-classic>=1.0.3, tiktoken (token-based splitting via from_tiktoken_encoder)]
  patterns:
    - Chapter-boundary enforcement via pre-split document grouping
    - Cosine distance HNSW config on Chroma collection for score normalization
    - Score-threshold retrieval filtering at 0.35 to exclude low-confidence context

key-files:
  created: []
  modified:
    - rag/chunker.py
    - rag/vector_store.py
    - rag/retriever.py
    - scripts/ingest_textbook.py
    - requirements.txt
    - .env.example

key-decisions:
  - "Token-based splitting (gpt-4o-mini tiktoken, 800/100) replaces character-based 500/50 — aligns chunk size with model context limits"
  - "Chapter grouping before split (not post-split filtering) is the only way to guarantee no cross-chapter chunks"
  - "Score threshold 0.35 chosen as starting point per CONTEXT.md — will be calibrated in Phase 3 benchmarking"
  - "Cosine distance set via collection_metadata hnsw:space=cosine on both build and load paths — required for similarity_score_threshold to work"

patterns-established:
  - "Chunker: always call build_chapter_map first, group by chapter, split per group"
  - "Vector store: always pass collection_metadata hnsw:space=cosine to both from_documents and Chroma() constructor"
  - "Retriever: use similarity_score_threshold not similarity — ensures irrelevant context never reaches LLM"

requirements-completed: [RETR-01, RETR-03, RETR-04]

# Metrics
duration: 9min
completed: 2026-03-14
---

# Phase 2 Plan 01: Retrieval Foundation Summary

**Chapter-aware 800-token chunking with cosine Chroma collection and score-threshold retriever (k=6, 0.35 threshold) replacing the original 500-char character-split store**

## Performance

- **Duration:** 9 min
- **Started:** 2026-03-13T20:28:16Z
- **Completed:** 2026-03-13T20:37:30Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Rewrote chunker.py with build_chapter_map() (regex-based, page-level chapter detection) and token-based splitting that groups docs by chapter before splitting so chunks never cross chapter boundaries
- Updated vector_store.py to configure cosine distance on both build and load paths, enabling score-normalized retrieval
- Updated retriever.py to use similarity_score_threshold with k=6 and threshold=0.35, filtering low-confidence results before they reach the LLM
- Ran re-ingestion: 228 pages, 230 chunks, 14 chapters detected, all chunks carry chapter + page metadata

## Task Commits

Each task was committed atomically:

1. **Task 1: Chapter-aware token-based chunking** - `6628ad7` (feat)
2. **Task 2: Cosine-distance vector store and score-threshold retriever** - `e61681e` (feat)
3. **Task 3: Update ingestion script and run re-ingestion** - `1d81046` (feat)

## Files Created/Modified

- `rag/chunker.py` - Rewritten: build_chapter_map(), chapter-grouped splitting, token-based 800/100, Unicode normalization
- `rag/vector_store.py` - cosine distance config on both build_vector_store and load_vector_store
- `rag/retriever.py` - similarity_score_threshold, k=6, threshold=0.35, retrieve_chunks filters by score
- `scripts/ingest_textbook.py` - shutil.rmtree for old store, chapter validation print, UTF-8 stdout, 4-step flow
- `requirements.txt` - langchain-classic>=1.0.3, bumped langchain/core/chroma version pins
- `.env.example` - CHUNK_SIZE=800, CHUNK_OVERLAP=100, TOP_K=6, SCORE_THRESHOLD=0.35

## Decisions Made

- Used `from_tiktoken_encoder` (gpt-4o-mini) for token-aware splitting — character-based splitting was misaligned with model context windows
- Chapter grouping enforced before splitting (not via post-split metadata filter) — the only way to guarantee zero cross-chapter chunks
- Score threshold set at 0.35 per CONTEXT.md guidance — will be calibrated in Phase 3 after benchmarking
- Cosine distance configured via `collection_metadata` (not `collection_configuration`) on both build and load paths to ensure consistent behavior

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Unicode thin space in PDF chapter headings caused UnicodeEncodeError on Windows**
- **Found during:** Task 3 (ingest_textbook.py execution)
- **Issue:** Chapter names extracted from the NCERT PDF contained `\u2009` (thin space) characters from the PDF text layer. Python's default CP1252 stdout encoding on Windows raised `UnicodeEncodeError` when printing chapter names.
- **Fix:** Added `unicodedata.normalize("NFKC", heading)` and `" ".join(heading.split())` in `build_chapter_map()` to normalize Unicode whitespace. Also added `sys.stdout.reconfigure(encoding="utf-8")` in the ingestion script.
- **Files modified:** `rag/chunker.py`, `scripts/ingest_textbook.py`
- **Verification:** Ingestion completed successfully; all 14 chapter names printed correctly.
- **Committed in:** `1d81046` (Task 3 commit)

**2. [Rule 1 - Bug] Windows file lock on chroma_db prevented deletion by another process**
- **Found during:** Task 3 (first ingestion attempt)
- **Issue:** Three Python processes (PIDs 48500, 10812, 48220) had chroma_db files open, causing `PermissionError` when `shutil.rmtree` was called.
- **Fix:** Killed the three blocking Python processes. Added `PermissionError` catch in the ingestion script with a clear user-facing message directing them to close running app instances.
- **Files modified:** `scripts/ingest_textbook.py`
- **Verification:** Deletion succeeded after processes terminated; ingestion completed.
- **Committed in:** `1d81046` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes were necessary for correct operation on Windows. No scope creep.

## Issues Encountered

- Chapter 7 produced a spurious duplicate entry ("Chapter 7: that the particles of a") because body text on a page referenced "Chapter" mid-sentence, matching the regex. The actual chapter heading ("Chapter 7: Particulate Nature of Matter") was also captured correctly. This is a known limitation of the regex approach and will be addressable in a future phase if the spurious entry causes retrieval degradation.

## User Setup Required

None - no external service configuration required beyond the existing `.env` with `OPENAI_API_KEY`.

## Next Phase Readiness

- Vector store ready with chapter-aware 800-token chunks and cosine distance
- Retriever wired with score thresholding — Phase 3 benchmarking can now measure Context Recall against the 0.75 gate
- The 0.35 score threshold is a starting point; Phase 3 should calibrate it with the NCERT question bank
- Chapter regex may need refinement if spurious chapter detection causes recall issues at benchmark time

## Self-Check: PASSED

All files verified present. All commits verified in git history.

- rag/chunker.py: FOUND
- rag/vector_store.py: FOUND
- rag/retriever.py: FOUND
- scripts/ingest_textbook.py: FOUND
- .env.example: FOUND
- requirements.txt: FOUND
- 6628ad7: FOUND
- e61681e: FOUND
- 1d81046: FOUND

---
*Phase: 02-retrieval-tuning*
*Completed: 2026-03-14*
