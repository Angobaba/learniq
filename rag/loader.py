"""
loader.py – Load a textbook PDF and return LangChain Document objects.
"""

import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


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
    if not pdf_path:
        raise ValueError("pdf_path must not be empty.")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"Textbook PDF not found at: {pdf_path}\n"
            "Please place your NCERT Class 8 Science PDF at that path and re-run "
            "the ingestion script."
        )

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents
