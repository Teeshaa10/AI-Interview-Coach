from google import genai

from app.core.config import get_settings
from app.db.mongo import get_database
from app.repositories.resume_analysis_repository import ResumeAnalysisRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.resume_analysis_service import ResumeAnalysisService


def get_resume_analysis_repository() -> ResumeAnalysisRepository:
    return ResumeAnalysisRepository(get_database())


def get_resume_repository() -> ResumeRepository:
    return ResumeRepository(get_database())


def get_gemini_client() -> genai.Client:
    settings = get_settings()

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )


def get_resume_analysis_service() -> ResumeAnalysisService:
    settings = get_settings()

    return ResumeAnalysisService(
        analysis_repository=get_resume_analysis_repository(),
        resume_repository=get_resume_repository(),
        gemini_client=get_gemini_client(),
        model_name=settings.GEMINI_MODEL_NAME,
    )