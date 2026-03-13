# LearnIQ

## What This Is

LearnIQ is an AI-powered, textbook-grounded tutor for CBSE Grade 8 Science. It turns the static NCERT textbook into a conversational, explainable learning experience using RAG over the textbook corpus with source citations. The product is being built toward school demos and progressively expands into adaptive quizzes, teacher analytics, bilingual support, and market-validation assets.

## Core Value

Students get accurate, grounded answers to Grade 8 Science questions drawn exclusively from the NCERT textbook, with visible citations and clear fallback when the answer is not found — zero hallucination tolerance.

## Requirements

### Validated

- [x] NCERT Grade 8 Science PDF ingestion into ChromaDB vector store — Phase 0-1
- [x] Chunking, embedding, and persistent vector store — Phase 0-1
- [x] Streamlit chat interface for student Q&A — Phase 1
- [x] Grounded answer generation with source citations — Phase 1
- [x] Fallback response when answer is not found in textbook — Phase 1
- [x] Environment configuration (.env, OpenAI API key) — Phase 0

### Active

- [ ] Retrieval quality tuning (chunk size ~800, overlap ~100, TOP_K ~6)
- [ ] Conversation-aware query rewriting for follow-up questions
- [ ] Benchmark dataset (15-20 textbook questions + 5 refusal tests)
- [ ] Retrieval precision/recall evaluation
- [ ] Citation quality improvement
- [ ] Adaptive quiz generation aligned with CBSE patterns
- [ ] Teacher dashboard with concept-level analytics
- [ ] Hindi/bilingual query support
- [ ] Market validation and GTM assets

### Out of Scope

- Page-aware lookup ("What is on page 65?") — semantic RAG only, not page-index retrieval
- Real-time chat/messaging — not core to tutoring value
- Mobile app — web-first via Streamlit
- OAuth/social login — no user accounts needed for school demos
- Video content — storage/bandwidth cost, not in scope

## Context

**Existing codebase:** Python RAG pipeline using LangChain + ChromaDB + OpenAI (GPT-4o-mini for generation, text-embedding-3-small for embeddings). Streamlit frontend. Phase 0-1 MVP is working locally.

**Known issues:**
- Follow-up queries fail because system treats each turn independently — no query rewriting
- Structure-based questions ("What are the types of friction?") retrieve poorly with current chunk size (500 tokens)
- Multi-turn chains like "Define friction -> types -> examples -> which helps walking" break down after first turn

**Data architecture principle:** Not all data goes into the same retrieval collection. Textbook teaches, assessment corpus tests, analytics data demonstrates, language layer translates, market data supports GTM. Each layer has separate storage and purpose.

**Near-term target:** School demos for teachers and administrators.

**Assessment data (CBSE syllabus, question banks, past papers):** Not yet sourced. Will need to be collected before Phase 3.

## Constraints

- **Tech stack**: Python, LangChain, ChromaDB, OpenAI APIs, Streamlit — already established
- **LLM**: OpenAI GPT-4o-mini (cost-efficient for student-facing answers)
- **Embeddings**: OpenAI text-embedding-3-small
- **Budget**: API cost sensitive — GPT-4o-mini chosen over GPT-4 for this reason
- **Data**: Single NCERT Grade 8 Science textbook (English) as primary corpus

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Separate data layers (textbook vs assessment vs analytics) | Different data serves different purposes; mixing degrades retrieval quality | -- Pending |
| ChromaDB for vector store | Lightweight, persistent, good for local MVP | -- Pending |
| GPT-4o-mini over GPT-4 | Cost efficiency for student-facing volume | -- Pending |
| Streamlit for UI | Fast prototyping, good for demos, Python-native | -- Pending |
| Phase 1 fix-up before Phase 2 | Retrieval tuning (chunking, TOP_K, query rewriting) is prerequisite for meaningful benchmarking | -- Pending |

---
*Last updated: 2026-03-14 after initialization*
