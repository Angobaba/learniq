"""
loader.py – Load source PDFs and return LangChain Document objects.

Supports loading a single PDF or scanning a directory for all PDFs.
Each document gets a ``source_name`` metadata field identifying which
file it came from (e.g. "NCERT Class 8 Science", "NCERT Exemplar").
"""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def _friendly_name(filename: str) -> str:
    """Turn a filename into a human-readable source label.

    Example: "NCERT_Class8_Science_English_Full.pdf" -> "NCERT Class8 Science English Full"
    """
    stem = Path(filename).stem
    return stem.replace("_", " ").replace("-", " ").strip()


def load_pdf(pdf_path: str, source_name: str | None = None) -> List[Document]:
    """Load a PDF file and return a list of LangChain Document objects.

    Each Document corresponds to one page of the PDF and includes metadata
    such as the source file path, page number, and source_name.

    Args:
        pdf_path: Absolute or relative path to the PDF file.
        source_name: Human-readable label for this source. If None,
            derived from the filename.

    Returns:
        A list of Document objects, one per page.
    """
    if not pdf_path:
        raise ValueError("pdf_path must not be empty.")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found at: {pdf_path}\n"
            "Please place the file at that path and re-run the ingestion script."
        )

    if source_name is None:
        source_name = _friendly_name(os.path.basename(pdf_path))

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    for doc in documents:
        doc.metadata["source_name"] = source_name

    return documents


def load_sources_dir(sources_dir: str) -> List[Document]:
    """Scan a directory (recursively) for all PDF files and load them.

    Each document's metadata includes ``source_name`` derived from the
    filename so that citations can show which source an answer came from.

    Args:
        sources_dir: Path to the directory containing PDF files.

    Returns:
        A combined list of Document objects from all PDFs found.

    Raises:
        FileNotFoundError: If the directory does not exist.
        ValueError: If no PDF files are found in the directory.
    """
    if not os.path.isdir(sources_dir):
        raise FileNotFoundError(f"Sources directory not found: {sources_dir}")

    pdf_files = sorted(Path(sources_dir).rglob("*.pdf"))

    if not pdf_files:
        raise ValueError(
            f"No PDF files found in {sources_dir}.\n"
            "Place your Grade 8 Science PDFs there and re-run."
        )

    all_docs: List[Document] = []
    for pdf_path in pdf_files:
        source_name = _friendly_name(pdf_path.name)
        docs = load_pdf(str(pdf_path), source_name=source_name)
        all_docs.extend(docs)

    return all_docs
