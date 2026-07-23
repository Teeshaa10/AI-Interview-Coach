import logging

from app.exceptions.resume import ResumeAccessDeniedError, ResumeNotFoundError, ResumeStorageError
from app.repositories.chroma_repository import ChunkMetadata, ChromaRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.embedding import EmbeddingSearchResult
from app.services.embedding_service import EmbeddingService
from app.utils.text_chunker import TextChunker

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Coordinates chunking, embedding generation, vector storage, and search."""

    def __init__(
        self,
        *,
        resume_repository: ResumeRepository,
        chroma_repository: ChromaRepository,
        embedding_service: EmbeddingService,
        chunker: TextChunker,
    ) -> None:
        self._resume_repository = resume_repository
        self._chroma_repository = chroma_repository
        self._embedding_service = embedding_service
        self._chunker = chunker

    async def index_resume(
        self,
        *,
        resume_id: str,
        user_id: str,
        filename: str,
        text: str,
    ) -> int:
        chunks = self._chunker.chunk(text)
        if not chunks:
            raise ResumeStorageError("No readable resume text was available for embedding")

        vectors = await self._embedding_service.embed_batch([chunk.text for chunk in chunks])
        metadata = [
            ChunkMetadata(
                user_id=user_id,
                resume_id=resume_id,
                chunk_index=chunk.index,
                filename=filename,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                char_count=chunk.char_count,
            )
            for chunk in chunks
        ]

        await self._chroma_repository.delete_by_resume(resume_id=resume_id, user_id=user_id)
        await self._chroma_repository.upsert_embeddings(
            ids=[f"{resume_id}:{chunk.index}" for chunk in chunks],
            embeddings=vectors,
            documents=[chunk.text for chunk in chunks],
            metadatas=metadata,
        )
        logger.info("Indexed resume %s into %d chunks", resume_id, len(chunks))
        return len(chunks)

    async def delete_resume_embeddings(self, *, resume_id: str, user_id: str) -> None:
        await self._chroma_repository.delete_by_resume(resume_id=resume_id, user_id=user_id)

    async def search(
        self,
        *,
        query: str,
        user_id: str,
        top_k: int,
        resume_id: str | None,
        min_similarity: float,
    ) -> list[EmbeddingSearchResult]:
        if resume_id:
            resume = await self._resume_repository.get_resume_by_id(resume_id)
            if resume is None:
                raise ResumeNotFoundError()
            if resume.user_id != user_id:
                raise ResumeAccessDeniedError()

        query_vector = await self._embedding_service.embed_text(query)
        matches = await self._chroma_repository.semantic_search(
            query_embedding=query_vector,
            user_id=user_id,
            top_k=top_k,
            resume_id=resume_id,
        )

        results: list[EmbeddingSearchResult] = []
        for match in matches:
            similarity = max(0.0, min(1.0, 1.0 - match["distance"]))
            if similarity < min_similarity:
                continue
            metadata = match["metadata"]
            results.append(
                EmbeddingSearchResult(
                    chunk_id=match["id"],
                    chunk_text=match["document"],
                    similarity_score=round(similarity, 6),
                    resume_id=str(metadata.get("resume_id", "")),
                    filename=str(metadata.get("filename", "")),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    start_char=int(metadata.get("start_char", 0)),
                    end_char=int(metadata.get("end_char", 0)),
                )
            )
        return results
