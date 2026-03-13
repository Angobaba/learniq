# LearnIQ – CBSE Grade 8 Science AI Tutor

> An AI-powered, textbook-grounded Q&A tutor for CBSE Grade 8 Science students, built with RAG (Retrieval-Augmented Generation), LangChain, ChromaDB, and Streamlit.

---

## Features

- 📚 Answers grounded **exclusively** in the NCERT Grade 8 Science textbook
- 🔍 Source citations (chapter / page) included with every answer
- 🛡️ Clear fallback when the answer is not found in the textbook
- 💬 Conversational Streamlit chat interface
- 🔁 ChromaDB persistence – embeddings built once and reused

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

---

## Project Structure

```
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
│   ├── raw/                   # Place your PDF here
│   ├── processed/             # Intermediate artefacts (optional)
│   └── benchmarks/
│       └── sample_benchmark.json
├── docs/
│   ├── architecture.md
│   └── prompt_guardrails.md
├── tests/
│   ├── test_retrieval.py
│   ├── test_citations.py
│   └── benchmark_runner.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- The NCERT Class 8 Science textbook PDF (not included in this repo for copyright reasons)

### 2. Clone and install

```bash
git clone https://github.com/Angobaba/learniq.git
cd learniq
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

Key variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `MODEL_NAME` | `gpt-4o-mini` | LLM model name |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `TEXTBOOK_PATH` | `./data/raw/NCERT_Class8_Science.pdf` | Path to textbook PDF |
| `TOP_K` | `4` | Number of chunks retrieved per query |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |

### 4. Add the textbook PDF

Place your NCERT Class 8 Science PDF at the path specified by `TEXTBOOK_PATH`:

```
data/raw/NCERT_Class8_Science.pdf
```

### 5. Ingest the textbook

Run the ingestion script **once** to build the vector store:

```bash
python scripts/ingest_textbook.py
```

This will:
- Load and parse the PDF
- Split it into overlapping chunks
- Embed each chunk using `text-embedding-3-small`
- Persist the ChromaDB store to `./chroma_db/`

### 6. Run the app

```bash
streamlit run app/streamlit_app.py
# or
bash scripts/run_app.sh
```

Open your browser at `http://localhost:8501`.

---

## Running Tests

```bash
pytest tests/test_retrieval.py tests/test_citations.py -v
```

## Running the Benchmark

After ingestion:

```bash
python tests/benchmark_runner.py --benchmark data/benchmarks/sample_benchmark.json
```

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for a detailed description of the system.

## Prompt Guardrails

See [docs/prompt_guardrails.md](docs/prompt_guardrails.md) for the answer-grounding rules enforced by the prompt.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch and PR rules.

---

## License

This project is for educational purposes. The NCERT textbook content is owned by NCERT and is not redistributed in this repository.
