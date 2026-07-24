from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.coding_dependencies import get_coding_repository
from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.interview_dependencies import get_gemini_client, get_interview_repository
from app.repositories.coaching_repository import CoachingRepository
from app.repositories.coding_interview_repository import CodingInterviewRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.resume_repository import ResumeRepository
from app.resume_dependencies import get_resume_repository
from app.services.coaching_service import CoachingService
from app.session_dependencies import get_session_management_service
from app.services.session_management_service import SessionManagementService


def get_coaching_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> CoachingRepository:
    return CoachingRepository(db)


def get_coaching_service(
    session_management_service: SessionManagementService = Depends(get_session_management_service),
    coaching_repository: CoachingRepository = Depends(get_coaching_repository),
    interview_repository: InterviewRepository = Depends(get_interview_repository),
    coding_repository: CodingInterviewRepository = Depends(get_coding_repository),
    resume_repository: ResumeRepository = Depends(get_resume_repository),
    gemini_client=Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
) -> CoachingService:
    return CoachingService(
        session_management_service=session_management_service,
        coaching_repository=coaching_repository,
        interview_repository=interview_repository,
        coding_repository=coding_repository,
        resume_repository=resume_repository,
        gemini_client=gemini_client,
        model_name=settings.GEMINI_MODEL_NAME,
    )
