import asyncio
import logging
from typing import Any

from chromadb import ClientAPI
from chromadb.api.models.Collection import Collection
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ChunkMetadata(BaseModel):
    user_id: str
    resume_id: str
    chunk_index: int
    filename: str
    start_char: int
    end_char: int
    char_count: int


class ChromaRepository:
    """Repository responsible for all ChromaDB operations."""

    def __init__(self, client: ClientAPI, collection_name: str) -> None:
        self._client = client
        self._collection_name = collection_name
        self._collection: Collection | None = None

    def _get_collection_sync(self) -> Collection:
        if self._collection is None:
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def create_collection(self) -> None:
        self._get_collection_sync()
        logger.info("Chroma collection '%s' ready", self._collection_name)

    async def upsert_embeddings(
        self,
        *,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[ChunkMetadata],
    ) -> None:
        if not ids:
            raise ValueError("At least one embedding is required")
        if not (len(ids) == len(embeddings) == len(documents) == len(metadatas)):
            raise ValueError("ids, embeddings, documents, and metadatas must have equal lengths")

        def _upsert() -> None:
            self._get_collection_sync().upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=[item.model_dump() for item in metadatas],
            )

        await asyncio.to_thread(_upsert)

    async def delete_by_resume(self, *, resume_id: str, user_id: str) -> None:
        def _delete() -> None:
            self._get_collection_sync().delete(
                where={
                    "$and": [
                        {"resume_id": {"$eq": resume_id}},
                        {"user_id": {"$eq": user_id}},
                    ]
                }
            )

        await asyncio.to_thread(_delete)

    async def semantic_search(
        self,
        *,
        query_embedding: list[float],
        user_id: str,
        top_k: int,
        resume_id: str | None = None,
    ) -> list[dict[str, Any]]:
        where: dict[str, Any]
        if resume_id:
            where = {
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"resume_id": {"$eq": resume_id}},
                ]
            }
        else:
            where = {"user_id": {"$eq": user_id}}

        def _query() -> dict[str, Any]:
            return self._get_collection_sync().query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"],
            )

        result = await asyncio.to_thread(_query)
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        return [
            {
                "id": ids[index],
                "document": documents[index],
                "metadata": metadatas[index] or {},
                "distance": float(distances[index]),
            }
            for index in range(len(ids))
        ]
