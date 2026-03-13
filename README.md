# LearnIQ

**AI Science Tutor for CBSE Grade 8**

LearnIQ answers student questions using NCERT Grade 8 Science study materials. Every answer is grounded in the source text with citations — no hallucination.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54-red)
![LangChain](https://img.shields.io/badge/LangChain-1.2-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5-orange)

---

## What It Does

- Answers Grade 8 Science questions grounded strictly in source materials
- Cites chapter name and page number with every answer
- Handles follow-up questions with automatic query rewriting
- Detects topic shifts so context doesn't bleed across subjects
- Shows expandable textbook passages so students can read the source
- Returns a friendly message when the answer isn't in the materials
- Supports multiple PDF sources — drop files into a folder and ingest

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/Angobaba/learniq.git
cd learniq
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

### 3. Add Source Materials

Place your Grade 8 Science PDFs in `data/raw/`:

```
data/raw/
  english/full_book/NCERT_Class8_Science_English_Full.pdf   (included)
  exemplar/NCERT_Exemplar_Grade8.pdf                        (optional)
  question_banks/CBSE_Previous_Year_Grade8.pdf              (optional)
```

Any PDF in `data/raw/` (including subfolders) will be automatically discovered and ingested.

### 4. Ingest

```bash
python scripts/ingest_textbook.py
```

This loads all PDFs, chunks them by chapter (800 tokens, 100 overlap), embeds them, and saves to ChromaDB. Each source is tagged so citations show which material the answer came from.

### 5. Run

```bash
streamlit run app/streamlit_app.py
```

Open **http://localhost:8501** in your browser.

---

## How It Works

```
Student Question
      |
      v
  Query Rewriting (follow-ups become standalone queries)
      |
      v
  Topic Shift Detection (cosine similarity on embeddings)
      |
      v
  Retrieval (ChromaDB, cosine distance, score threshold 0.35, top-6)
      |
      v
  Answer Generation (grounded in retrieved chunks only)
      |
      v
  Citations + Expandable Passages
```

**Key design decisions:**
- Chunks never cross chapter boundaries — each chunk belongs to one chapter
- Score thresholding filters out low-relevance chunks before the LLM sees them
- Binary confidence: either a cited answer or a clear "not found" — no gray zone
- Dual session state: display messages (Streamlit) and LangChain message objects are kept separate

---

## Project Structure

```
learniq/
├── app/
│   └── streamlit_app.py         # Chat interface (dark theme UI)
├── rag/
│   ├── loader.py                # PDF loading + multi-source directory scan
│   ├── chunker.py               # Chapter-aware token-based chunking
│   ├── embeddings.py            # OpenAI embedding wrapper
│   ├── vector_store.py          # ChromaDB with cosine distance
│   ├── retriever.py             # Score-threshold retriever (k=6)
│   ├── qa_chain.py              # Conversational RAG chain + topic shift
│   └── prompts.py               # System prompts and fallback messages
├── scripts/
│   ├── ingest_textbook.py       # Multi-source ingestion pipeline
│   ├── run_app.sh               # App launcher
│   └── setup_and_run.sh         # Ingest + run in one command
├── data/
│   ├── raw/                     # Drop PDFs here (scanned recursively)
│   ├── processed/
│   └── benchmarks/
├── .streamlit/
│   └── config.toml              # Dark theme configuration
├── .env.example
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit (custom dark theme) |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| RAG Framework | LangChain (langchain-classic) |
| Vector Store | ChromaDB (persistent, cosine distance) |
| PDF Loading | PyPDF via LangChain |
| Chunking | RecursiveCharacterTextSplitter (tiktoken, 800 tokens) |

---

## Adding More Sources

Just drop PDFs into `data/raw/` and re-run ingestion:

```bash
# Add your files to any subfolder under data/raw/
cp new_material.pdf data/raw/

# Re-ingest everything
python scripts/ingest_textbook.py
```

The ingestion script will:
- Find all PDFs recursively in `data/raw/`
- Tag each with a source name derived from the filename
- Chunk by chapter with metadata (chapter, page, source)
- Rebuild the vector store

Citations in the app will show which source the answer came from.

---

## Roadmap

- [x] **Phase 0-1: MVP** — RAG pipeline, chat UI, citations, fallback
- [x] **Phase 2: Retrieval Tuning** — Chapter-aware chunking, query rewriting, score thresholding, multi-turn support
- [ ] **Phase 3: Benchmarking** — RAGAS evaluation, Context Recall >= 0.75 gate
- [ ] **Phase 4: Quiz Foundation** — Chapter-aligned MCQs and short-answer questions
- [ ] **Phase 5: Adaptive Quizzes** — Weak concept tagging, difficulty adaptation
- [ ] **Phase 6: Teacher Dashboard** — Concept heatmap, mastery trends
- [ ] **Phase 7: Demo Hardening** — Error handling, caching, latency optimization
- [ ] **Phase 8: Hindi Support** — Translate-first bilingual pipeline

---

## License

MIT
