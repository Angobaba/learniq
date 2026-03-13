#!/usr/bin/env bash
# run_app.sh – Start the LearnIQ Streamlit app.
#
# Prerequisites:
#   1. Install dependencies:  pip install -r requirements.txt
#   2. Copy .env.example to .env and set your OPENAI_API_KEY.
#   3. Run the ingestion script once:
#        python scripts/ingest_textbook.py
#
# Usage:
#   bash scripts/run_app.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if [ ! -f ".env" ]; then
  echo "WARNING: .env file not found. Copy .env.example to .env and set your OPENAI_API_KEY."
fi

echo "Starting LearnIQ…"
streamlit run app/streamlit_app.py
