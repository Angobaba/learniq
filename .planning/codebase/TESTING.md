# Testing Patterns

**Analysis Date:** 2026-03-13

## Test Framework

**Runner:**
- pytest 8.0.0+ (specified in `requirements.txt`)
- Standard Python `unittest` module used throughout (test files inherit from `unittest.TestCase`)
- Config: No `pytest.ini`, `pyproject.toml`, or `setup.cfg` detected - uses pytest defaults

**Assertion Library:**
- Standard `unittest` assertions: `self.assertEqual()`, `self.assertTrue()`, `self.assertFalse()`, `self.assertIn()`, `self.assertGreater()`, `self.assertIsInstance()`, `self.assertRaises()`

**Run Commands:**
```bash
pytest tests/                    # Run all tests
python -m pytest tests/ -v       # Verbose output
python -m unittest discover      # Via unittest discovery
python tests/test_retrieval.py   # Run specific test file
```

## Test File Organization

**Location:**
- Co-located in `tests/` directory at project root
- Not co-located with source code (separate from `rag/`, `app/`, `scripts/`)

**Naming:**
- Test files: `test_*.py` - `test_retrieval.py`, `test_citations.py`, `benchmark_runner.py`
- Test classes: `Test*` - `TestChunker`, `TestRetriever`, `TestLoader`, `TestCitationExtraction`, `TestAnswerQuestion`, `TestContextFormatting`
- Test methods: `test_*` - `test_chunk_splits_long_document()`, `test_citations_extracted_correctly()`

**Structure:**
```
tests/
├── __init__.py              # Package marker (single comment)
├── test_retrieval.py        # Unit tests for rag modules (loader, chunker, retriever)
├── test_citations.py        # Unit tests for citation extraction and QA chain
└── benchmark_runner.py      # Integration/evaluation tests against benchmark dataset
```

## Test Structure

**Suite Organization:**

```python
class TestChunker(unittest.TestCase):
    """Tests for rag/chunker.py."""

    def test_chunk_splits_long_document(self):
        from rag.chunker import chunk_documents
        # ... test body
```

**Patterns:**
- Each module under test has its own `Test*` class
- Docstring on test class describes what's being tested
- Imports happen inside test methods (lazy imports for clarity and isolation)
- Simple setup (no `setUp()` or `tearDown()` methods observed)
- Helper methods prefixed with underscore: `_make_mock_store()`, `_make_doc()`

**Common Test Structure:**
```python
def test_function_name(self):
    from module import function
    # Arrange
    input_data = setup()
    # Act
    result = function(input_data)
    # Assert
    self.assertEqual(result, expected)
```

## Mocking

**Framework:** `unittest.mock` (standard library)

**Patterns:**

```python
from unittest.mock import MagicMock, patch

# Create mock object
store = MagicMock()
store.similarity_search.return_value = docs
store.as_retriever.return_value = MagicMock()

# Verify calls
store.similarity_search.assert_called_once_with("test query", k=3)

# Mock return values
mock_llm = MagicMock()
mock_response = MagicMock()
mock_response.content = "Photosynthesis is..."
mock_llm.invoke.return_value = mock_response
```

**What to Mock:**
- External services: ChromaDB (Chroma store), OpenAI API (ChatOpenAI, embeddings)
- Heavy dependencies: PyPDFLoader (replaced by mock in unit tests)
- Helper methods for isolation: `_make_mock_store()`, `_make_doc()` create test fixtures
- Both locations: `tests/test_retrieval.py` lines 55-60, `tests/test_citations.py` lines 20-21, 74-77

**What NOT to Mock:**
- Core retrieval logic: `retrieve_chunks()` calls the real mock store
- Document chunking: `chunk_documents()` uses real splitter (fast)
- Citation extraction: `_extract_citations()` runs without mocks (pure function)
- Formatting: `_format_context()` runs without mocks

## Fixtures and Factories

**Test Data:**

```python
# Helper method in test class
def _make_doc(self, content, source, page):
    return Document(page_content=content, metadata={"source": source, "page": page})

# Usage in test
doc = self._make_doc("Plants make food.", "book.pdf", 10)

# Or inline
doc = Document(
    page_content="Some textbook content about photosynthesis.",
    metadata={"source": "test.pdf", "page": 5},
)
```

**Location:**
- Fixtures defined as helper methods within test classes (no separate fixture modules)
- Helper methods use underscore prefix: `_make_mock_store()`, `_make_doc()`
- Used in: `tests/test_retrieval.py` (lines 55-60), `tests/test_citations.py` (lines 20-21, 59-60)

## Coverage

**Requirements:** No coverage requirements detected - no `.coveragerc`, no coverage thresholds in config

**View Coverage:**
```bash
pytest --cov=rag tests/           # Generate coverage report
pytest --cov=rag --cov-report=html tests/  # HTML report
coverage report                   # View coverage stats
```

## Test Types

**Unit Tests:**
- Scope: Individual functions in isolation (`load_pdf()`, `chunk_documents()`, `retrieve_chunks()`, `_extract_citations()`, `_format_context()`, `answer_question()`)
- Approach: Mock external dependencies (Chroma store, LLM), test logic directly
- Files: `tests/test_retrieval.py` (38 lines of test logic after imports), `tests/test_citations.py` (96 lines of test logic)
- Example: `test_chunk_splits_long_document()` creates synthetic document, calls chunker, verifies result count

**Integration Tests:**
- Scope: Full pipeline from question → retrieval → answer generation
- Approach: Uses real ChromaDB and OpenAI (requires .env configuration)
- File: `tests/benchmark_runner.py` (123 lines)
- Pattern: Loads benchmark questions from JSON, retrieves chunks, generates answers, checks for expected keywords
- Execution: `python tests/benchmark_runner.py [--benchmark data/benchmarks/sample_benchmark.json]`

**E2E Tests:**
- Not found in codebase
- Manual testing via Streamlit UI: `streamlit run app/streamlit_app.py`

## Common Patterns

**Async Testing:**
- Not applicable - no async/await in codebase
- All functions are synchronous

**Error Testing:**

```python
def test_load_missing_file_raises(self):
    from rag.loader import load_pdf

    with self.assertRaises(FileNotFoundError):
        load_pdf("/nonexistent/path/book.pdf")

def test_load_empty_path_raises(self):
    from rag.loader import load_pdf

    with self.assertRaises(ValueError):
        load_pdf("")
```

Used in: `tests/test_retrieval.py` lines 90-100

**Return Type Verification:**

```python
def test_retrieve_returns_list(self):
    from rag.retriever import retrieve_chunks

    docs = [Document(...)]
    store = self._make_mock_store(docs)
    results = retrieve_chunks(store, "test query", top_k=2)
    self.assertIsInstance(results, list)

def test_chunk_returns_documents(self):
    from rag.chunker import chunk_documents

    doc = Document(page_content="Short text.", metadata={})
    chunks = chunk_documents([doc])
    self.assertIsInstance(chunks, list)
    for chunk in chunks:
        self.assertIsInstance(chunk, Document)
```

Used in: `tests/test_retrieval.py` lines 62-49

**Metadata Preservation:**

```python
def test_chunk_preserves_metadata(self):
    from rag.chunker import chunk_documents

    doc = Document(
        page_content="Some textbook content about photosynthesis.",
        metadata={"source": "test.pdf", "page": 5},
    )
    chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=50)
    self.assertTrue(len(chunks) >= 1)
    self.assertEqual(chunks[0].metadata["source"], "test.pdf")
```

Used in: `tests/test_retrieval.py` lines 31-40

**Deduplication Testing:**

```python
def test_citations_deduplication(self):
    from rag.qa_chain import _extract_citations

    chunks = [
        self._make_doc("a", "book.pdf", 1),
        self._make_doc("b", "book.pdf", 1),
        self._make_doc("c", "book.pdf", 1),
    ]
    citations = _extract_citations(chunks)
    self.assertEqual(len(citations), 1)
```

Used in: `tests/test_citations.py` lines 35-44

## Test Execution Context

**Path Setup:**
All test files add repo root to sys.path:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
```

This allows imports like `from rag.chunker import chunk_documents` from within tests.

**Environment:**
Tests that don't use real services (test_retrieval.py, test_citations.py) run without .env configuration.
Integration tests (benchmark_runner.py) load .env via `load_dotenv()` and require OPENAI_API_KEY, CHROMA_PERSIST_DIR.

**Test Independence:**
- Each test is independent (no shared state between tests)
- Mocks are created fresh per test method
- No database or file system state persists

---

*Testing analysis: 2026-03-13*
