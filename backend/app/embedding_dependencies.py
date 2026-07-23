from typing import Annotated

from chromadb import ClientAPI
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.db.chroma import get_chroma_client
from app.db.mongo import get_database
from app.repositories.chroma_repository import ChromaRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.services.semantic_search_service import SemanticSearchService
from app.utils.text_chunker import TextChunker


def get_embedding_resume_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> ResumeRepository:
    return ResumeRepository(database)


def get_chroma_repository(
    client: Annotated[ClientAPI, Depends(get_chroma_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChromaRepository:
    return ChromaRepository(client=client, collection_name=settings.CHROMA_COLLECTION_NAME)


def get_text_chunker(settings: Annotated[Settings, Depends(get_settings)]) -> TextChunker:
    return TextChunker(
        chunk_size=settings.EMBEDDING_CHUNK_SIZE,
        chunk_overlap=settings.EMBEDDING_CHUNK_OVERLAP,
    )


def get_semantic_search_service(
    resume_repository: Annotated[ResumeRepository, Depends(get_embedding_resume_repository)],
    chroma_repository: Annotated[ChromaRepository, Depends(get_chroma_repository)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    chunker: Annotated[TextChunker, Depends(get_text_chunker)],
) -> SemanticSearchService:
    return SemanticSearchService(
        resume_repository=resume_repository,
        chroma_repository=chroma_repository,
        embedding_service=embedding_service,
        chunker=chunker,
    )


__all__ = [
    "get_chroma_repository",
    "get_embedding_service",
    "get_semantic_search_service",
    "get_text_chunker",
]
