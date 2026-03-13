# Coding Conventions

**Analysis Date:** 2026-03-13

## Naming Patterns

**Files:**
- Lowercase with underscores: `loader.py`, `vector_store.py`, `qa_chain.py`
- Descriptive names matching functionality: `ingest_textbook.py`, `benchmark_runner.py`
- Module organization: `rag/` contains vector retrieval logic, `app/` contains UI, `scripts/` contains CLI tooling

**Functions:**
- Lowercase with underscores: `load_pdf()`, `chunk_documents()`, `retrieve_chunks()`
- Private functions prefixed with underscore: `_format_context()`, `_extract_citations()`, `_make_mock_store()`
- Main entry points named `main()`: `scripts/ingest_textbook.py`, `tests/benchmark_runner.py`

**Variables:**
- Lowercase with underscores for clarity: `chunk_size`, `persist_dir`, `top_k`, `mock_llm`, `expected_keywords`
- Loop variables: `doc`, `chunk`, `c`, `kw` (short names for simple iteration)
- Dictionary keys as plain strings: `"source"`, `"page"`, `"content"`, `"answer"`, `"citations"`, `"found"`

**Types:**
- Modern Python type hints throughout: `List[Document]`, `str | None`, `Dict`
- Return types explicitly annotated: `-> List[Document]`, `-> Chroma`, `-> Dict`, `-> None`
- Union types use pipe syntax (`|`): `str | None`, `int | None`, `ChatOpenAI | None`

## Code Style

**Formatting:**
- Line length: reasonable (~80-100 characters observed)
- Indentation: 4 spaces (Python standard)
- No automated formatter detected (Black, autopep8) - formatting is manual but consistent

**Linting:**
- No linting configuration file detected (no .pylintrc, pyproject.toml with tool.pylint)
- No pre-commit hooks detected
- Code follows PEP 8 conventions organically

## Import Organization

**Order:**
1. Standard library: `import os`, `import sys`, `import json`, `import argparse`, `import time`, `import types`, `import unittest`, `from typing import ...`
2. Third-party: `import streamlit`, `from dotenv import load_dotenv`, `from langchain_*`
3. Local/relative: `from rag.loader import`, `from rag.chunker import`

**Path Aliases:**
- No path aliases detected (no `@` prefix imports)
- Relative imports from package root achieved via sys.path manipulation:
  ```python
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
  ```
- Used consistently in: `app/streamlit_app.py` (line 18), `scripts/ingest_textbook.py` (line 25), `tests/test_retrieval.py` (line 15), `tests/test_citations.py` (line 12)

## Error Handling

**Patterns:**
- Raise with descriptive messages: `raise ValueError("pdf_path must not be empty.")` in `rag/loader.py`
- Exceptions caught and logged: `except FileNotFoundError as exc:` in `scripts/ingest_textbook.py` (line 59)
- Broad exception catching in UI for user feedback: `except Exception as exc:` in `app/streamlit_app.py` (line 163), followed by error display
- Early returns for guards: `if not pdf_path: raise ValueError(...)`
- Error messages include context and next steps: "Please copy .env.example to .env and add your API key" in `rag/embeddings.py` (line 29)

## Logging

**Framework:** `print()` statements only - no dedicated logging library (no logging module, no loguru)

**Patterns:**
- Status messages with decorative formatting: `print("=" * 60)` in `scripts/ingest_textbook.py` (line 35)
- Timestamped progress: `t0 = time.time(); ... print(f"Done in {time.time() - t0:.1f}s")` in `scripts/ingest_textbook.py`
- Error prefix `[ERROR]` and step prefix `[1/3]` for clarity in `scripts/ingest_textbook.py`
- Streamlit status messages: `st.success()`, `st.error()`, `st.warning()` for UI in `app/streamlit_app.py`

## Comments

**When to Comment:**
- Docstrings on all public functions with clear Args, Returns, Raises sections
- Section headers with dashes for organizational clarity: `# ---------------------------------------------------------------------------`
- Comments for non-obvious logic (rare - most code is self-explanatory)
- No verbose inline comments; logic is typically clear from function names

**JSDoc/TSDoc:**
- Python docstrings used throughout (not JSDoc - this is Python)
- Format: triple-quoted docstring immediately after function definition
- Style: Google-style docstrings with sections for Args, Returns, Raises
- Examples from `rag/loader.py`:
  ```python
  def load_pdf(pdf_path: str) -> List[Document]:
      """Load a PDF file and return a list of LangChain Document objects.

      Each Document corresponds to one page of the PDF and includes metadata
      such as the source file path and page number.

      Args:
          pdf_path: Absolute or relative path to the PDF file.

      Returns:
          A list of Document objects, one per page.

      Raises:
          FileNotFoundError: If the PDF file does not exist at the given path.
          ValueError: If the PDF path is empty or None.
      """
  ```

## Function Design

**Size:** Functions are small and focused
- Most functions: 10-40 lines
- Longest: `answer_question()` in `rag/qa_chain.py` is 46 lines but includes comprehensive docstring
- Private helpers extracted: `_format_context()`, `_extract_citations()` separate formatting logic

**Parameters:**
- Functions accept required parameters followed by optional ones with defaults
- Optional parameters often read from environment if not supplied:
  ```python
  def chunk_documents(
      documents: List[Document],
      chunk_size: int | None = None,
      chunk_overlap: int | None = None,
  ) -> List[Document]:
      if chunk_size is None:
          chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
  ```
- Maximum observed: 4 parameters (typical: 1-3)

**Return Values:**
- Single return type clearly specified: `-> List[Document]`, `-> Chroma`, `-> None`
- Complex returns use dictionaries with explicit keys:
  ```python
  return {
      "answer": answer_text,
      "citations": citations,
      "found": True,
  }
  ```
- All return paths explicitly documented in docstring

## Module Design

**Exports:**
- All public functions and classes are used directly (no `__all__` declarations found)
- Private functions prefixed with underscore by convention: `_format_context`, `_extract_citations`, `_make_mock_store`
- Import what you need directly: `from rag.loader import load_pdf`

**Barrel Files:**
- Minimal `__init__.py` files - just package markers with single comment: `# rag package`, `# app package`
- No re-exports in `__init__.py`
- Direct imports from specific modules required

**Constants:**
- Uppercase for module-level constants: `COLLECTION_NAME = "learniq_textbook"` in `rag/vector_store.py`
- Multi-line string constants for prompts: `SYSTEM_PROMPT`, `NO_CONTEXT_RESPONSE` in `rag/prompts.py`
- Environment variable defaults inline: `os.getenv("MODEL_NAME", "gpt-4o-mini")`

---

*Convention analysis: 2026-03-13*
