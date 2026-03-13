"""
benchmark_runner.py – Evaluate LearnIQ retrieval and QA quality against a
benchmark dataset stored in data/benchmarks/.

The benchmark file format is a JSON array of objects:
    [
      {
        "question": "...",
        "expected_keywords": ["...", "..."],
        "chapter": "...",
        "notes": "optional"
      },
      ...
    ]

Usage:
    python tests/benchmark_runner.py [--benchmark data/benchmarks/sample_benchmark.json]

Environment variables:
    OPENAI_API_KEY, MODEL_NAME, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, TOP_K
    (same as the main app – load from .env)

The script:
1. Loads the benchmark JSON.
2. For each question, retrieves chunks and generates an answer.
3. Checks whether any of the expected_keywords appear in the answer.
4. Prints a summary with per-question pass/fail and an overall score.

This is a starter scaffold – extend with semantic similarity scoring, RAGAS,
or other metrics as the project matures.
"""

import argparse
import json
import os
import sys
from typing import Dict, List

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()


def run_benchmark(benchmark_path: str) -> None:
    """Run evaluation against the benchmark file at *benchmark_path*."""
    # Lazy imports so the module is importable even without installed deps
    from rag.vector_store import load_vector_store
    from rag.retriever import retrieve_chunks
    from rag.qa_chain import build_qa_chain, answer_question

    if not os.path.exists(benchmark_path):
        print(f"[ERROR] Benchmark file not found: {benchmark_path}")
        sys.exit(1)

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    print(f"Loaded {len(benchmark)} benchmark question(s) from {benchmark_path}\n")

    try:
        vector_store = load_vector_store()
        llm = build_qa_chain()
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    results: List[Dict] = []

    for i, item in enumerate(benchmark, start=1):
        question = item.get("question", "")
        expected_keywords = [kw.lower() for kw in item.get("expected_keywords", [])]
        chapter = item.get("chapter", "Unknown chapter")

        print(f"[{i}/{len(benchmark)}] {question}")

        chunks = retrieve_chunks(vector_store, question)
        result = answer_question(question, chunks, llm)

        answer_lower = result["answer"].lower()
        matched = [kw for kw in expected_keywords if kw in answer_lower]
        passed = len(matched) > 0 if expected_keywords else result["found"]

        status = "PASS" if passed else "FAIL"
        print(f"        Status   : {status}")
        print(f"        Chapter  : {chapter}")
        print(f"        Found    : {result['found']}")
        if expected_keywords:
            print(f"        Keywords matched: {matched} / {expected_keywords}")
        print()

        results.append(
            {
                "question": question,
                "passed": passed,
                "found": result["found"],
                "answer": result["answer"],
                "citations": result["citations"],
            }
        )

    # Summary
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    pct = (100 * passed_count / total) if total > 0 else 0
    print("=" * 60)
    print(f"Benchmark complete: {passed_count}/{total} passed ({pct:.0f}%)")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="LearnIQ Benchmark Runner")
    parser.add_argument(
        "--benchmark",
        default="data/benchmarks/sample_benchmark.json",
        help="Path to the benchmark JSON file",
    )
    args = parser.parse_args()
    run_benchmark(args.benchmark)


if __name__ == "__main__":
    main()
