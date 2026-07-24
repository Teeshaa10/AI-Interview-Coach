import asyncio
import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from app.core.config import get_settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Converts text into embedding vectors using a SentenceTransformer model.

    Both the library import and model creation are delayed until embeddings
    are requested. This keeps FastAPI startup lightweight.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = (
            model_name or get_settings().EMBEDDING_MODEL_NAME
        )
        self._model: Any | None = None
        self._load_lock = asyncio.Lock()

    def _load_model_sync(self) -> Any:
        """
        Import sentence-transformers and load the model only on first use.
        """

        logger.info(
            "Importing sentence-transformers and loading model '%s'",
            self._model_name,
        )

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(self._model_name)

        logger.info("Embedding model loaded and ready")
        return model

    async def _get_model(self) -> Any:
        if self._model is not None:
            return self._model

        async with self._load_lock:
            if self._model is None:
                loop = asyncio.get_running_loop()
                self._model = await loop.run_in_executor(
                    None,
                    self._load_model_sync,
                )

        return self._model

    async def embed_text(self, text: str) -> list[float]:
        vectors = await self.embed_batch([text])
        return vectors[0]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        model = await self._get_model()
        loop = asyncio.get_running_loop()

        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
            ),
        )

        logger.debug("Embedded %d text chunk(s)", len(texts))
        return embeddings.tolist()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()