# LearnIQ – CBSE Grade 8 Science AI Tutor

> LearnIQ is an AI-powered, textbook-grounded tutor for CBSE Grade 8 Science. It begins as a retrieval-based Q&A tutor using the NCERT textbook and evolves into a broader learning system with adaptive quizzes, teacher dashboards, bilingual support, and GTM-ready validation assets.

---

## Vision

LearnIQ aims to turn static school textbooks into an interactive, explainable, and personalized learning experience.

The product starts with a narrow but important promise:

- answer student questions from the NCERT Grade 8 Science textbook
- cite the source clearly
- avoid unsupported hallucinated answers

Over time, LearnIQ expands into:

- retrieval quality benchmarking
- adaptive quizzes aligned with CBSE patterns
- teacher dashboards and insight views
- Hindi / bilingual experiences
- market validation and GTM assets

---

## Current Status

Current repo status: **Phase 1 MVP is working locally**

Completed:
- NCERT Grade 8 Science textbook ingestion
- chunking, embeddings, and persistent ChromaDB vector store
- Streamlit chat interface
- grounded answer generation with citations
- fallback response when answer is not found in textbook

Current focus:
- improve retrieval quality
- strengthen follow-up handling
- add benchmarks and evaluation
- prepare for quiz and dashboard phases

---

## Project Phases

## Phase 0 — Setup and Foundation

This phase establishes the technical and product foundations.

### Goals
- define MVP scope
- set up repository and branch strategy
- configure environment variables
- prepare source textbook corpus
- create ingestion pipeline
- validate local setup
- define benchmark questions

### Outputs
- working repo scaffold
- `.env` configuration
- merged NCERT full-book PDF
- ingestion pipeline
- ChromaDB vector store
- initial benchmark plan

---

## Phase 1 — Textbook-Grounded Q&A MVP

This is the current core product milestone.

### Goals
- answer student questions using only the NCERT Grade 8 Science textbook
- retrieve relevant chunks using embeddings
- generate grounded answers with citations
- clearly refuse when answer is not found in the textbook
- provide a simple conversational UI for students

### Features
- PDF ingestion
- chunking and embedding
- persistent ChromaDB vector store
- top-k retrieval
- grounded answer generation
- source citations in the UI
- Streamlit-based frontend

### Success Criteria
- reliable answers for common textbook questions
- low hallucination rate
- clear citation display
- stable local demo experience

---

## Phase 2 — Retrieval Quality and Benchmarking

This phase improves answer quality, trust, and debugability.

### Goals
- improve chunking strategy
- improve retrieval precision and recall
- tune `TOP_K`, chunk size, and overlap
- benchmark common textbook questions
- debug follow-up question behavior

### Planned Work
- benchmark dataset for textbook questions
- retrieval testing
- citation validation
- chunk inspection
- prompt tuning
- light multi-turn query rewriting / history support

### Success Criteria
- fewer false fallbacks
- better answer consistency
- stronger performance on concept flows and multi-turn queries

---

## Phase 3 — Adaptive Quiz Layer

This phase expands LearnIQ from answering to active learning.

### Goals
- generate quiz questions aligned with textbook concepts and CBSE patterns
- evaluate student responses
- adapt difficulty based on performance
- support chapter-level practice and revision

### Planned Data Sources
- CBSE syllabus
- question banks
- past year question papers

### Planned Features
- MCQ generation
- short-answer question generation
- quiz scoring
- concept-level weakness tagging
- revision recommendations

### Success Criteria
- quiz quality aligns with curriculum expectations
- meaningful variation in difficulty
- useful student practice flow

---

## Phase 4 — Teacher Dashboard and Analytics

This phase adds value for teachers and school demos.

### Goals
- visualize student weaknesses
- surface repeated concept confusion
- show chapter-level mastery trends
- demonstrate class-level learning insights

### Planned Data Sources
- synthetic student interaction logs initially
- later real anonymized session data

### Planned Features
- weak-topic heatmap
- repeated-question detection
- chapter mastery summary
- performance trends
- teacher-facing demo dashboard

### Success Criteria
- clear teacher value proposition
- useful class-level views
- strong demo story beyond chatbot functionality

---

## Phase 5 — Hindi / Bilingual Support

This phase adds accessibility and product differentiation.

### Goals
- support Hindi queries
- support bilingual / Hinglish interaction
- improve accessibility for Indian learners
- strengthen demos with localized interaction

### Planned Approach
- query normalization / translation layer
- bilingual retrieval support
- optional Hindi textbook support
- answer translation back to Hindi

### Success Criteria
- basic Hindi support works reliably
- stronger demo appeal
- improved accessibility for non-English-first learners

---

## Phase 6 — Market Validation and GTM Assets

This phase supports external storytelling and scale readiness.

### Goals
- prepare market validation narrative
- support parent / school demos
- create investor-facing proof points
- ground opportunity sizing using credible education datasets

### Planned Data Sources
- ASER
- UDISE+
- RedSeer
- other education ecosystem references

### Outputs
- GTM documents
- deck inputs
- validation notes
- market opportunity framing

---

## Features

### Current Features
- 📚 Answers grounded **exclusively** in the NCERT Grade 8 Science textbook
- 🔍 Source citations included with every answer
- 🛡️ Clear fallback when answer is not found in the textbook
- 💬 Conversational Streamlit chat interface
- 🔁 ChromaDB persistence — embeddings built once and reused

### Planned Features
- 🧪 Retrieval benchmarking and tuning
- 📝 Adaptive quizzes and chapter practice
- 👩‍🏫 Teacher dashboard and analytics
- 🌐 Hindi / bilingual support
- 📊 Market validation and GTM assets

---

## Data Architecture

Not all project data is used in the same way. LearnIQ separates data into multiple layers.

### 1. Core Textbook Corpus
Used for student-facing answers.

Includes:
- NCERT Grade 8 Science textbook
- later possibly Hindi Science textbook

### 2. Assessment Corpus
Used for quiz generation and alignment.

Includes:
- CBSE syllabus
- question bank
- past year papers

### 3. Analytics Dataset
Used for dashboard and teacher insights.

Includes:
- synthetic student interactions
- later anonymized session logs

### 4. Language Layer
Used for Hindi / bilingual experiences.

Includes:
- translation or NLP services
- later bilingual textbook handling

### 5. Market Validation Layer
Used for GTM and pitch materials.

Includes:
- ASER
- UDISE+
- RedSeer

### Design Principle
- textbook teaches
- assessment corpus tests
- analytics data demonstrates
- language layer translates
- market data supports GTM

---

## Tech Stack

| Component | Library / Service |
|-----------|-------------------|
| UI | Streamlit |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| RAG framework | LangChain |
| Vector store | ChromaDB (persistent) |
| PDF loading | PyPDF (via LangChain) |
| Language support (planned) | Bhashini / translation layer |
| Analytics storage (planned) | JSON / CSV / SQLite / Postgres |

---

## Project Structure

```text
learniq/
├── app/
│   └── streamlit_app.py       # Main chat interface
├── rag/
│   ├── loader.py              # PDF loader
│   ├── chunker.py             # Text splitter
│   ├── embeddings.py          # Embedding helper
│   ├── vector_store.py        # ChromaDB create/load
│   ├── retriever.py           # Top-k chunk retrieval
│   ├── qa_chain.py            # Grounded answer generation
│   └── prompts.py             # System prompts / guardrails
├── scripts/
│   ├── ingest_textbook.py     # One-time ingestion pipeline
│   └── run_app.sh             # App launcher
├── data/
│   ├── raw/
│   │   ├── english/
│   │   │   └── full_book/
│   │   ├── hindi/
│   │   ├── assessment/
│   │   ├── analytics/
│   │   └── market/
│   ├── processed/             # Intermediate artefacts (optional)
│   └── benchmarks/
│       └── sample_benchmark.json
├── docs/
│   ├── architecture.md
│   ├── prompt_guardrails.md
│   └── roadmap.md
├── tests/
│   ├── test_retrieval.py
│   ├── test_citations.py
│   └── benchmark_runner.py
├── .env.example
├── requirements.txt
├── CONTRIBUTING.md
└── README.md