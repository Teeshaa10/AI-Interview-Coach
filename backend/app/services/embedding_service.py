import asyncio
import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Turns text into embedding vectors using all-MiniLM-L6-v2.

    This class knows nothing about ChromaDB, Mongo, or resumes — it only
    converts strings to vectors. That separation means the embedding model
    could be swapped, upgraded, or reused for something outside the RAG
    pipeline entirely without ChromaRepository or any calling service
    needing to change.
    """

    def __init__(self, model_name: str | None = None) -> None:
        # The model is intentionally NOT loaded here. all-MiniLM-L6-v2 is
        # ~90MB and takes real time to load from disk (or download, on
        # first run). Loading it in __init__ would mean paying that cost
        # at import time — slowing down app startup and every test that
        # imports this module, even ones that never touch embeddings.
        # _get_model() below loads it lazily, on first actual use.
        self._model_name = model_name or get_settings().EMBEDDING_MODEL_NAME
        self._model: SentenceTransformer | None = None

        # Guards model loading against a race: if two requests both call
        # embed_batch() before the model has finished loading, this lock
        # ensures the second request awaits the first request's in-flight
        # load instead of starting a redundant second one.
        self._load_lock = asyncio.Lock()

    def _load_model_sync(self) -> SentenceTransformer:
        """The actual blocking load. Kept as a plain sync method so it can
        be handed to run_in_executor as-is."""
        logger.info("Loading embedding model '%s' (first use)", self._model_name)
        model = SentenceTransformer(self._model_name)
        logger.info("Embedding model loaded and ready")
        return model

    async def _get_model(self) -> SentenceTransformer:
        """
        Returns the loaded model, loading it on the first call.

        The load happens inside loop.run_in_executor, not directly on the
        event loop — SentenceTransformer's constructor does real disk I/O
        and CPU work (reading and initializing model weights), and running
        that synchronously on the event loop would freeze every other
        request the server is handling for the duration of the load.
        """
        if self._model is not None:
            return self._model

        async with self._load_lock:
            # Re-check inside the lock: another request may have finished
            # loading the model while this one was waiting to acquire it.
            if self._model is None:
                loop = asyncio.get_running_loop()
                self._model = await loop.run_in_executor(None, self._load_model_sync)
        return self._model

    async def embed_text(self, text: str) -> list[float]:
        """
        Embeds a single string.

        Implemented as a thin wrapper around embed_batch so there is
        exactly one code path that actually calls the model — a single
        text is just a batch of one.
        """
        vectors = await self.embed_batch([text])
        return vectors[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Embeds a list of strings in a single model call.

        Batching is a real performance concern, not just convenience:
        SentenceTransformer processes a batch far more efficiently than
        the same number of one-at-a-time calls, because the forward pass
        vectorizes across the whole batch instead of paying fixed
        per-call overhead. Any caller embedding multiple resume/JD chunks
        (the normal case) should call this once with the full list rather
        than looping embed_text().
        """
        if not texts:
            return []

        model = await self._get_model()
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: model.encode(texts, convert_to_numpy=True, show_progress_bar=False),
        )
        logger.debug(f"Embedded {len(texts)} text chunk(s)")
        return embeddings.tolist()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """
    Returns the process-wide EmbeddingService singleton.

    Follows the exact same pattern as get_settings() in app/core/config.py:
    lru_cache guarantees EmbeddingService() is constructed exactly once per
    process, and every caller — including every
    Depends(get_embedding_service) — receives that same instance. This is
    what makes the lazy-loaded model actually stay loaded and reused
    across requests instead of reloading on every call.
    """
    return EmbeddingService()
