import logging

import chromadb
from chromadb import ClientAPI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ChromaDB:
    """Owns the single Chroma client for the process's lifetime — same
    reasoning as MongoDB above: one client, one place to manage its
    lifecycle."""

    client: ClientAPI | None = None


chromadb_wrapper = ChromaDB()


def connect_to_chroma() -> None:
    """
    Opens the Chroma client. Called once, at application startup.

    We use PersistentClient, which stores vectors on local disk at
    CHROMA_PERSIST_DIR instead of requiring a separate Chroma server
    process. That's the right choice for now — it needs zero extra
    infrastructure to run locally or on Render. If the project ever
    outgrows a single-disk vector store, this function is the only place
    that changes: swap PersistentClient for HttpClient pointing at a
    hosted Chroma instance, and every service using get_chroma_client()
    below is unaffected.

    Unlike Mongo, PersistentClient connects synchronously and raises
    immediately on failure, so no separate health ping is needed here.
    """
    settings = get_settings()
    chromadb_wrapper.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    logger.info(f"Connected to ChromaDB at '{settings.CHROMA_PERSIST_DIR}'")


def get_chroma_client() -> ClientAPI:
    """FastAPI dependency exposing the Chroma client to routes and
    services, mirroring get_database() for the same testability reason."""
    if chromadb_wrapper.client is None:
        raise RuntimeError("ChromaDB is not connected. Was connect_to_chroma() called?")
    return chromadb_wrapper.client
