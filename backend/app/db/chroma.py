import logging
from pathlib import Path

import chromadb
from chromadb import ClientAPI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ChromaDB:
    """Own the single ChromaDB client used by the application process."""

    client: ClientAPI | None = None


chromadb_wrapper = ChromaDB()


def connect_to_chroma() -> None:
    """Create the persistent ChromaDB client during application startup."""

    if chromadb_wrapper.client is not None:
        logger.info("ChromaDB is already connected")
        return

    settings = get_settings()
    persist_directory = Path(settings.CHROMA_PERSIST_DIR)
    persist_directory.mkdir(parents=True, exist_ok=True)

    chromadb_wrapper.client = chromadb.PersistentClient(
        path=str(persist_directory)
    )

    logger.info("Connected to ChromaDB at '%s'", persist_directory)


def get_chroma_client() -> ClientAPI:
    """Return the initialized ChromaDB client."""

    if chromadb_wrapper.client is None:
        raise RuntimeError(
            "ChromaDB is not connected. Was connect_to_chroma() called?"
        )

    return chromadb_wrapper.client


def close_chroma_connection() -> None:
    """Release the process-level ChromaDB client reference on shutdown."""

    if chromadb_wrapper.client is None:
        return

    chromadb_wrapper.client = None
    logger.info("ChromaDB connection closed")