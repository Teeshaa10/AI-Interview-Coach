from fastapi import Depends
from google import genai
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.interview_dependencies import get_gemini_client
from app.repositories.coding_interview_repository import CodingInterviewRepository
from app.services.code_execution_providers.judge0 import Judge0Provider
from app.services.code_execution_providers.piston import PistonProvider
from app.services.code_execution_service import CodeExecutionService
from app.services.coding_interview_service import CodingInterviewService


def get_coding_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> CodingInterviewRepository:
    return CodingInterviewRepository(db)


def get_code_execution_service(settings: Settings = Depends(get_settings)) -> CodeExecutionService:
    provider_name = settings.CODE_EXECUTION_PROVIDER.lower().strip()
    provider = None
    if provider_name == "piston" and settings.PISTON_BASE_URL.strip():
        provider = PistonProvider(settings.PISTON_BASE_URL, settings.CODE_EXECUTION_TIMEOUT_SECONDS)
    elif provider_name == "judge0" and settings.JUDGE0_BASE_URL.strip():
        provider = Judge0Provider(
            settings.JUDGE0_BASE_URL,
            settings.JUDGE0_API_KEY,
            settings.JUDGE0_API_HOST,
            settings.CODE_EXECUTION_TIMEOUT_SECONDS,
        )
    return CodeExecutionService(provider)


def get_coding_interview_service(
    repository: CodingInterviewRepository = Depends(get_coding_repository),
    execution_service: CodeExecutionService = Depends(get_code_execution_service),
    gemini_client: genai.Client | None = Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
) -> CodingInterviewService:
    return CodingInterviewService(
        repository=repository,
        execution_service=execution_service,
        gemini_client=gemini_client,
        model_name=settings.GEMINI_MODEL_NAME,
        timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
        max_source_length=settings.CODE_MAX_SOURCE_LENGTH,
    )
