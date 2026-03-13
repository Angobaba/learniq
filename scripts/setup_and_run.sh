#!/usr/bin/env bash
# setup_and_run.sh – Run the LearnIQ execution sequence: ensure setup, ingest if needed, then start the app.
#
# Sequence (see docs/execution_sequence.md):
#   1. Check .env and OPENAI_API_KEY
#   2. If ChromaDB store is missing, run ingestion
#   3. Start the Streamlit app
#
# Usage:
#   bash scripts/setup_and_run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if [ ! -f ".env" ]; then
  echo "WARNING: .env not found. Copy .env.example to .env and set OPENAI_API_KEY."
  echo "Then run this script again."
  exit 1
fi

# Default ChromaDB path (matches .env.example). Use CHROMA_PERSIST_DIR in .env for custom path.
CHROMA_DIR="./chroma_db"

# Run ingestion if ChromaDB store does not exist
if [ ! -d "$CHROMA_DIR" ] || [ -z "$(ls -A "$CHROMA_DIR" 2>/dev/null)" ]; then
  echo "ChromaDB store not found at $CHROMA_DIR. Running ingestion..."
  python scripts/ingest_textbook.py
  echo ""
fi

echo "Starting LearnIQ…"
exec streamlit run app/streamlit_app.py
