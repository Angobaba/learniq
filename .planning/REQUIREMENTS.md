# Requirements: LearnIQ

**Defined:** 2026-03-14
**Core Value:** Students get accurate, grounded answers to Grade 8 Science questions from the NCERT textbook with citations and zero hallucination tolerance.

## v1 Requirements

Requirements for current milestone. Each maps to roadmap phases.

### Retrieval Quality

- [ ] **RETR-01**: System uses optimized chunk size (~800 tokens) and overlap (~100 tokens) for textbook prose
- [ ] **RETR-02**: System rewrites follow-up queries using conversation history before retrieval
- [ ] **RETR-03**: System applies relevance score thresholding to filter low-quality retrieved chunks
- [ ] **RETR-04**: System returns top-k results with tuned k value (~6) for better recall
- [ ] **RETR-05**: Citations display chapter name and page reference alongside answer text
- [ ] **RETR-06**: System handles multi-turn question chains (e.g., define -> types -> examples -> application)

### Benchmarking

- [ ] **BENCH-01**: Benchmark dataset of 15-20 direct textbook questions with expected answers
- [ ] **BENCH-02**: Benchmark dataset of 5+ refusal tests for out-of-scope questions
- [ ] **BENCH-03**: Benchmark dataset of 5+ multi-turn question chains
- [ ] **BENCH-04**: Benchmark dataset of 5+ comparative/explanatory questions
- [ ] **BENCH-05**: Automated benchmark runner that measures retrieval precision and answer quality
- [ ] **BENCH-06**: Context Recall score >= 0.75 on benchmark before advancing to quiz phase

### Quiz and Assessment

- [ ] **QUIZ-01**: System generates chapter-aligned MCQs from textbook content
- [ ] **QUIZ-02**: System generates short-answer questions from textbook content
- [ ] **QUIZ-03**: System evaluates student responses and provides scoring
- [ ] **QUIZ-04**: System tags weak concepts based on incorrect answers
- [ ] **QUIZ-05**: System recommends revision paths based on weak concept tags
- [ ] **QUIZ-06**: Quiz difficulty adapts based on student performance within a session
- [ ] **QUIZ-07**: Student can select chapter/topic for focused practice

### Teacher Dashboard

- [ ] **DASH-01**: Dashboard displays weak-topic heatmap across chapters
- [ ] **DASH-02**: Dashboard shows repeated-question detection patterns
- [ ] **DASH-03**: Dashboard presents chapter-level mastery summary
- [ ] **DASH-04**: Dashboard visualizes performance trends over sessions
- [ ] **DASH-05**: Dashboard uses synthetic student interaction data for initial demo
- [ ] **DASH-06**: Dashboard is accessible via a separate Streamlit page or tab

### Bilingual Support

- [ ] **LANG-01**: System accepts Hindi-language queries and translates to English for retrieval
- [ ] **LANG-02**: System accepts Hinglish (mixed Hindi-English) queries
- [ ] **LANG-03**: System can respond in Hindi when queried in Hindi
- [ ] **LANG-04**: Translation layer does not degrade retrieval quality compared to English queries

### Demo Readiness

- [ ] **DEMO-01**: Error handling shows user-friendly messages, not raw Python exceptions
- [ ] **DEMO-02**: ChromaDB vector store is loaded once and cached, not reloaded per query
- [ ] **DEMO-03**: Streamlit UI has chapter/topic navigation for guided exploration
- [ ] **DEMO-04**: App loads and responds within acceptable demo latency (< 5 seconds per answer)

## v2 Requirements

Deferred to future milestone. Tracked but not in current roadmap.

### Market Validation and GTM

- **GTM-01**: ASER/UDISE+ data analysis for market sizing
- **GTM-02**: Investor-facing proof points and deck inputs
- **GTM-03**: Parent/school demo narrative and validation assets
- **GTM-04**: RedSeer and education ecosystem data integration

### Advanced Features

- **ADV-01**: Page-aware retrieval mode using page metadata
- **ADV-02**: Hindi textbook ingestion as separate corpus
- **ADV-03**: Real student interaction logging (anonymized)
- **ADV-04**: Multi-grade support beyond Grade 8
- **ADV-05**: CBSE assertion-reason question format support

## Out of Scope

| Feature | Reason |
|---------|--------|
| Video content | Storage/bandwidth costs, not core to tutoring value |
| OAuth/social login | No user accounts needed for school demos |
| Mobile app | Web-first via Streamlit, mobile deferred |
| Multi-corpus Q&A retrieval | Assessment data serves quiz generation, not student Q&A |
| Real-time chat/messaging | Not core to tutoring interaction |
| Page-number lookup | Semantic RAG only; page-aware retrieval is v2 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RETR-01 | Phase 2 | Pending |
| RETR-02 | Phase 2 | Pending |
| RETR-03 | Phase 2 | Pending |
| RETR-04 | Phase 2 | Pending |
| RETR-05 | Phase 2 | Pending |
| RETR-06 | Phase 2 | Pending |
| BENCH-01 | Phase 3 | Pending |
| BENCH-02 | Phase 3 | Pending |
| BENCH-03 | Phase 3 | Pending |
| BENCH-04 | Phase 3 | Pending |
| BENCH-05 | Phase 3 | Pending |
| BENCH-06 | Phase 3 | Pending |
| QUIZ-01 | Phase 4 | Pending |
| QUIZ-02 | Phase 4 | Pending |
| QUIZ-03 | Phase 4 | Pending |
| QUIZ-04 | Phase 5 | Pending |
| QUIZ-05 | Phase 5 | Pending |
| QUIZ-06 | Phase 5 | Pending |
| QUIZ-07 | Phase 4 | Pending |
| DASH-01 | Phase 6 | Pending |
| DASH-02 | Phase 6 | Pending |
| DASH-03 | Phase 6 | Pending |
| DASH-04 | Phase 6 | Pending |
| DASH-05 | Phase 6 | Pending |
| DASH-06 | Phase 6 | Pending |
| LANG-01 | Phase 8 | Pending |
| LANG-02 | Phase 8 | Pending |
| LANG-03 | Phase 8 | Pending |
| LANG-04 | Phase 8 | Pending |
| DEMO-01 | Phase 7 | Pending |
| DEMO-02 | Phase 7 | Pending |
| DEMO-03 | Phase 7 | Pending |
| DEMO-04 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-03-14*
*Last updated: 2026-03-14 — traceability filled after roadmap creation*
