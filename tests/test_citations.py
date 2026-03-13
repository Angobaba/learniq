"""
test_citations.py – Unit tests for citation extraction and the QA chain.

Uses mocked LLM and retriever so no API key or live services are required.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.documents import Document


class TestCitationExtraction(unittest.TestCase):
    """Tests for citation logic in rag/qa_chain.py."""

    def _make_doc(self, content, source, page):
        return Document(page_content=content, metadata={"source": source, "page": page})

    def test_citations_extracted_correctly(self):
        from rag.qa_chain import _extract_citations

        chunks = [
            self._make_doc("Plants make food.", "book.pdf", 10),
            self._make_doc("Chlorophyll absorbs light.", "book.pdf", 10),
            self._make_doc("Roots absorb water.", "book.pdf", 15),
        ]
        citations = _extract_citations(chunks)
        # Two unique (source, page) combos
        self.assertEqual(len(citations), 2)

    def test_citations_deduplication(self):
        from rag.qa_chain import _extract_citations

        chunks = [
            self._make_doc("a", "book.pdf", 1),
            self._make_doc("b", "book.pdf", 1),
            self._make_doc("c", "book.pdf", 1),
        ]
        citations = _extract_citations(chunks)
        self.assertEqual(len(citations), 1)

    def test_citation_keys_present(self):
        from rag.qa_chain import _extract_citations

        chunks = [self._make_doc("text", "NCERT.pdf", 42)]
        citations = _extract_citations(chunks)
        self.assertIn("source", citations[0])
        self.assertIn("page", citations[0])
        self.assertEqual(citations[0]["page"], 42)


class TestAnswerQuestion(unittest.TestCase):
    """Tests for rag/qa_chain.answer_question."""

    def _make_doc(self, content, source="book.pdf", page=1):
        return Document(page_content=content, metadata={"source": source, "page": page})

    def test_no_chunks_returns_not_found(self):
        from rag.qa_chain import answer_question
        from rag.prompts import NO_CONTEXT_RESPONSE

        result = answer_question("What is gravity?", chunks=[])
        self.assertFalse(result["found"])
        self.assertEqual(result["answer"], NO_CONTEXT_RESPONSE)
        self.assertEqual(result["citations"], [])

    def test_with_chunks_calls_llm(self):
        from rag.qa_chain import answer_question

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Photosynthesis is the process by which plants make food."
        mock_llm.invoke.return_value = mock_response

        chunks = [self._make_doc("Plants make food through photosynthesis.")]
        result = answer_question("What is photosynthesis?", chunks=chunks, llm=mock_llm)

        self.assertTrue(result["found"])
        self.assertIn("Photosynthesis", result["answer"])
        self.assertEqual(len(result["citations"]), 1)

    def test_result_structure(self):
        from rag.qa_chain import answer_question

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Some answer.")

        result = answer_question("question", [self._make_doc("context")], llm=mock_llm)
        self.assertIn("answer", result)
        self.assertIn("citations", result)
        self.assertIn("found", result)


class TestContextFormatting(unittest.TestCase):
    """Tests for the _format_context helper."""

    def test_format_includes_page(self):
        from rag.qa_chain import _format_context

        doc = Document(page_content="Cell is the unit of life.", metadata={"source": "book.pdf", "page": 3})
        context = _format_context([doc])
        self.assertIn("Page: 3", context)
        self.assertIn("Cell is the unit of life.", context)

    def test_format_multiple_chunks(self):
        from rag.qa_chain import _format_context

        docs = [
            Document(page_content="chunk 1", metadata={"source": "a.pdf", "page": 1}),
            Document(page_content="chunk 2", metadata={"source": "a.pdf", "page": 2}),
        ]
        context = _format_context(docs)
        self.assertIn("[1]", context)
        self.assertIn("[2]", context)


if __name__ == "__main__":
    unittest.main()
