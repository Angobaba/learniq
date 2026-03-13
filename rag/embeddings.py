"""
embeddings.py – Create and return the OpenAI embedding model.
"""

import os

from langchain_openai import OpenAIEmbeddings


def get_embeddings(model: str | None = None) -> OpenAIEmbeddings:
    """Return an OpenAIEmbeddings instance.

    The embedding model name is read from the EMBEDDING_MODEL environment
    variable if not supplied explicitly (default: text-embedding-3-small).

    Args:
        model: The OpenAI embedding model name to use.

    Returns:
        An OpenAIEmbeddings instance ready for use with LangChain vector stores.

    Raises:
        ValueError: If OPENAI_API_KEY is not set in the environment.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Please copy .env.example to .env and add your API key."
        )

    if model is None:
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    return OpenAIEmbeddings(model=model, openai_api_key=api_key)
