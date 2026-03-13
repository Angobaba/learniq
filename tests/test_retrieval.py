"""
test_retrieval.py – Unit tests for the retrieval pipeline.

These tests use a lightweight in-memory mock so they do not require an
OpenAI API key or a live ChromaDB instance.
"""

import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# Ensure repo root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.documents import Document


class TestChunker(unittest.TestCase):
    """Tests for rag/chunker.py."""

    def test_chunk_splits_long_document(self):
        from rag.chunker import chunk_documents

        text = "word " * 300  # ~1500 characters
        doc = Document(page_content=text, metadata={"source": "test.pdf", "page": 1})
        chunks = chunk_documents([doc], chunk_size=200, chunk_overlap=20)
        self.assertGreater(len(chunks), 1, "Long document should produce multiple chunks")

    def test_chunk_preserves_metadata(self):
        from rag.chunker import chunk_documents

        doc = Document(
            page_content="Some textbook content about photosynthesis.",
            metadata={"source": "test.pdf", "page": 5},
        )
        chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=50)
        self.assertTrue(len(chunks) >= 1)
        self.assertEqual(chunks[0].metadata["source"], "test.pdf")

    def test_chunk_returns_documents(self):
        from rag.chunker import chunk_documents

        doc = Document(page_content="Short text.", metadata={})
        chunks = chunk_documents([doc])
        self.assertIsInstance(chunks, list)
        for chunk in chunks:
            self.assertIsInstance(chunk, Document)


class TestRetriever(unittest.TestCase):
    """Tests for rag/retriever.py."""

    def _make_mock_store(self, docs):
        """Return a mock Chroma store that returns *docs* on similarity_search."""
        store = MagicMock()
        store.similarity_search.return_value = docs
        store.as_retriever.return_value = MagicMock()
        return store

    def test_retrieve_returns_list(self):
        from rag.retriever import retrieve_chunks

        docs = [
            Document(page_content="Photosynthesis occurs in chloroplasts.", metadata={"source": "book.pdf", "page": 10}),
        ]
        store = self._make_mock_store(docs)
        results = retrieve_chunks(store, "What is photosynthesis?", top_k=2)
        self.assertIsInstance(results, list)

    def test_retrieve_calls_similarity_search(self):
        from rag.retriever import retrieve_chunks

        store = self._make_mock_store([])
        retrieve_chunks(store, "test query", top_k=3)
        store.similarity_search.assert_called_once_with("test query", k=3)

    def test_retrieve_empty_store(self):
        from rag.retriever import retrieve_chunks

        store = self._make_mock_store([])
        results = retrieve_chunks(store, "anything", top_k=4)
        self.assertEqual(results, [])


class TestLoader(unittest.TestCase):
    """Tests for rag/loader.py."""

    def test_load_missing_file_raises(self):
        from rag.loader import load_pdf

        with self.assertRaises(FileNotFoundError):
            load_pdf("/nonexistent/path/book.pdf")

    def test_load_empty_path_raises(self):
        from rag.loader import load_pdf

        with self.assertRaises(ValueError):
            load_pdf("")


if __name__ == "__main__":
    unittest.main()
