from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from google import genai

from app.core.config import Settings, get_settings
from app.embedding_dependencies import get_semantic_search_service
from app.services.interview_service import InterviewService
from app.services.semantic_search_service import SemanticSearchService


async def get_gemini_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncIterator[genai.Client | None]:
    """Provide a request-scoped official Google GenAI client and close it safely."""

    api_key = settings.GEMINI_API_KEY.strip()
    if not api_key:
        yield None
        return

    client = genai.Client(api_key=api_key)
    try:
        yield client
    finally:
        await client.aio.aclose()


def get_interview_service(
    semantic_search_service: Annotated[
        SemanticSearchService,
        Depends(get_semantic_search_service),
    ],
    gemini_client: Annotated[genai.Client | None, Depends(get_gemini_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> InterviewService:
    return InterviewService(
        semantic_search_service=semantic_search_service,
        gemini_client=gemini_client,
        model_name=settings.GEMINI_MODEL_NAME,
        search_top_k=settings.INTERVIEW_SEARCH_TOP_K,
        timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
    )
