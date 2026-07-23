from fastapi import Depends
from google import genai
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.repositories.interview_repository import InterviewRepository
from app.resume_dependencies import get_semantic_search_service
from app.services.evaluation_service import EvaluationService
from app.services.interview_service import InterviewService
from app.services.semantic_search_service import SemanticSearchService


def get_interview_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> InterviewRepository:
    return InterviewRepository(db)


def get_gemini_client(
    settings: Settings = Depends(get_settings),
) -> genai.Client | None:
    if not settings.GEMINI_API_KEY.strip():
        return None

    return genai.Client(api_key=settings.GEMINI_API_KEY)


def get_interview_service(
    semantic_search_service: SemanticSearchService = Depends(
        get_semantic_search_service
    ),
    gemini_client: genai.Client | None = Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
) -> InterviewService:
    return InterviewService(
        semantic_search_service=semantic_search_service,
        gemini_client=gemini_client,
        model_name=settings.GEMINI_MODEL_NAME,
        search_top_k=settings.INTERVIEW_SEARCH_TOP_K,
        timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
    )


def get_evaluation_service(
    gemini_client: genai.Client | None = Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
) -> EvaluationService:
    return EvaluationService(
        gemini_client=gemini_client,
        model_name=settings.GEMINI_MODEL_NAME,
        timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
    )