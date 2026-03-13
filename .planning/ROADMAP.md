# Roadmap: LearnIQ

## Overview

LearnIQ's Phase 0-1 MVP is working — students can ask questions and get cited, grounded answers from the NCERT Grade 8 Science textbook. This roadmap covers the next seven phases that transform that working prototype into a school-demo-ready product with adaptive quizzes, teacher analytics, and Hindi language support. The dependency chain is strict: retrieval quality must be solid before benchmarking validates it, benchmarks must pass before quiz generation is built, quiz data must exist before teacher analytics has anything to display, and the entire English stack must be proven before a bilingual layer is added.

## Milestones

- [x] **v0-1 MVP** - Phases 0-1 (shipped — RAG pipeline, chat UI, citations, fallback)
- [ ] **v1.1 Demo-Ready Tutor** - Phases 2-7 (in progress)

## Phases

**Phase Numbering:**
- Phase 0-1 are complete (MVP shipped)
- This roadmap starts at Phase 2

- [x] **Phase 0-1: MVP** - NCERT ingestion, RAG pipeline, Streamlit chat, citations, fallback (DONE)
- [ ] **Phase 2: Retrieval Tuning** - Fix chunk size, query rewriting, TOP_K, relevance thresholding, and citation display
- [ ] **Phase 3: Benchmarking and Quality Gate** - Build benchmark dataset, run RAGAS evaluation, enforce Context Recall >= 0.75 gate
- [ ] **Phase 4: Quiz Foundation** - Generate chapter-aligned MCQs and short-answer questions, score responses, add chapter selector
- [ ] **Phase 5: Adaptive Quiz and Concept Tracking** - Tag weak concepts, recommend revision paths, adapt difficulty within session
- [ ] **Phase 6: Teacher Dashboard** - Weak-concept heatmap, chapter mastery summary, performance trends using synthetic session data
- [ ] **Phase 7: Demo Hardening** - Friendly error handling, vector store caching, topic navigation, latency target < 5 seconds
- [ ] **Phase 8: Hindi / Bilingual Support** - Translate-first Hindi query pipeline, Hinglish support, Hindi response generation

## Phase Details

### Phase 2: Retrieval Tuning
**Goal**: The retrieval layer returns complete, relevant textbook passages for both direct questions and multi-turn follow-up queries
**Depends on**: Phase 1 (MVP)
**Requirements**: RETR-01, RETR-02, RETR-03, RETR-04, RETR-05, RETR-06
**Success Criteria** (what must be TRUE):
  1. A student asks "What about in animals?" after a question about plants — the system retrieves animal-related chunks rather than triggering the fallback response
  2. A multi-turn chain of four questions ("Define friction -> What are its types? -> Give examples -> Which type helps us walk?") produces a coherent, textbook-grounded answer at every turn
  3. Citations display a human-readable chapter name and page reference (e.g., "Chapter 12: Friction, Page 148") rather than a raw file path
  4. When the retriever finds no chunks above the relevance threshold, the system returns a clear "not found" response rather than a low-confidence partial answer
  5. Re-ingestion with chunk size ~800 tokens and overlap ~100 tokens is complete and the vector store reflects the new settings
**Plans:** 2 plans
Plans:
- [x] 02-01-PLAN.md — Chapter-aware 800-token chunking, cosine vector store, score-threshold retriever (RETR-01, RETR-03, RETR-04)
- [ ] 02-02-PLAN.md — Conversational RAG chain with query rewriting, multi-turn, citation display, fallback (RETR-02, RETR-05, RETR-06)

### Phase 3: Benchmarking and Quality Gate
**Goal**: Retrieval quality is measurably validated against a representative dataset, and no further phases begin until the quality gate passes
**Depends on**: Phase 2
**Requirements**: BENCH-01, BENCH-02, BENCH-03, BENCH-04, BENCH-05, BENCH-06
**Success Criteria** (what must be TRUE):
  1. A benchmark dataset of at least 30 questions exists covering: direct definitions, multi-sentence concept questions, multi-turn sequences, refusal tests for out-of-scope questions, and comparative/explanatory questions
  2. Running the benchmark runner produces a report with RAGAS Context Recall, Faithfulness, and Answer Relevancy scores
  3. Context Recall score is >= 0.75 on the benchmark dataset (hard gate — Phase 4 does not start below this threshold)
  4. The benchmark runner can be re-run after any retrieval change and produces a comparable score output
**Plans**: TBD

### Phase 4: Quiz Foundation
**Goal**: Students can take a chapter-aligned quiz that generates questions from the textbook, evaluates responses, and shows grounded feedback
**Depends on**: Phase 3 (quality gate must pass)
**Requirements**: QUIZ-01, QUIZ-02, QUIZ-03, QUIZ-07
**Success Criteria** (what must be TRUE):
  1. A student selects a chapter from the UI and receives a quiz with MCQ and short-answer questions drawn from that chapter's textbook content
  2. Every quiz question is anchored to a retrieved textbook chunk — no question contains a distractor or answer not derivable from the NCERT Grade 8 Science textbook
  3. After submitting a response, the student sees whether their answer was correct or incorrect, along with a hint pointing to the relevant textbook passage
  4. The quiz can be started for any of the 18 NCERT Grade 8 Science chapters
**Plans**: TBD

### Phase 5: Adaptive Quiz and Concept Tracking
**Goal**: The quiz remembers what a student struggles with and adjusts accordingly, producing a session-level weak-concept summary
**Depends on**: Phase 4
**Requirements**: QUIZ-04, QUIZ-05, QUIZ-06
**Success Criteria** (what must be TRUE):
  1. After answering several quiz questions, the student sees a session-level summary listing concepts they answered incorrectly (e.g., "Review: Types of Friction, Pressure in Fluids")
  2. The system recommends specific textbook sections or chapters for revision based on the concepts tagged as weak
  3. Within a single session, the quiz presents harder questions on topics the student has answered correctly and easier questions on topics the student has answered incorrectly
**Plans**: TBD

### Phase 6: Teacher Dashboard
**Goal**: A teacher opening the dashboard sees which concepts are most frequently missed across students, presented visually using synthetic session data
**Depends on**: Phase 5
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06
**Success Criteria** (what must be TRUE):
  1. A teacher navigates to a separate dashboard page or tab in the Streamlit app without leaving the main student interface
  2. The dashboard displays a heatmap or table showing which chapters and concepts have the highest incorrect answer rates across synthetic student sessions
  3. The dashboard shows a chapter-level mastery summary (e.g., Chapter 11: 62% mastery across students)
  4. The dashboard highlights repeated questions — topics that students ask about most frequently in the Q&A interface
  5. Performance trends over multiple sessions are visible (e.g., concept X improved from 40% to 65% over the last 5 sessions)
**Plans**: TBD

### Phase 7: Demo Hardening
**Goal**: The app handles errors gracefully, loads fast, and survives a live school demo on a mobile hotspot without showing a Python exception to a teacher
**Depends on**: Phase 6
**Requirements**: DEMO-01, DEMO-02, DEMO-03, DEMO-04
**Success Criteria** (what must be TRUE):
  1. Disconnecting the internet and submitting a question shows a friendly, non-technical message — no Python exception class names, file paths, or stack traces are visible to the user
  2. The second question in a session responds at least 2 seconds faster than the first because the vector store is loaded once at startup and cached, not reloaded per query
  3. A teacher navigating by chapter or topic can reach any of the 18 NCERT chapters via the UI without typing a query
  4. From app load to displayed answer, the total response time is under 5 seconds on a mobile hotspot connection for typical textbook questions
**Plans**: TBD

### Phase 8: Hindi / Bilingual Support
**Goal**: A student can ask a question in Hindi or Hinglish and receive a grounded, textbook-accurate answer in Hindi without degraded retrieval quality
**Depends on**: Phase 7
**Requirements**: LANG-01, LANG-02, LANG-03, LANG-04
**Success Criteria** (what must be TRUE):
  1. A student types "प्रकाश संश्लेषण क्या है?" and receives a grounded Hindi answer citing the correct textbook chapter — the retriever finds the relevant English chunks via translate-first architecture, not cross-lingual embedding matching
  2. A student types a Hinglish query like "friction ke types kya hain?" and receives a coherent, grounded answer
  3. When a query is in Hindi, the full response is in Hindi — there is no mid-answer language switch to English
  4. Retrieval quality on a 15-question Hindi benchmark is not measurably worse than the equivalent English benchmark (within 10% on Context Recall)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 2 → 3 → 4 → 5 → 6 → 7 → 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 2. Retrieval Tuning | 1/2 | In progress | - |
| 3. Benchmarking and Quality Gate | 0/TBD | Not started | - |
| 4. Quiz Foundation | 0/TBD | Not started | - |
| 5. Adaptive Quiz and Concept Tracking | 0/TBD | Not started | - |
| 6. Teacher Dashboard | 0/TBD | Not started | - |
| 7. Demo Hardening | 0/TBD | Not started | - |
| 8. Hindi / Bilingual Support | 0/TBD | Not started | - |

---
*Roadmap created: 2026-03-14*
*Coverage: 33/33 v1 requirements mapped*
