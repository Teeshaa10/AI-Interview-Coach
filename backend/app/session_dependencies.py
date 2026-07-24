from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.coding_dependencies import get_coding_repository
from app.db.mongo import get_database
from app.interview_dependencies import get_gemini_client, get_interview_repository
from app.report_dependencies import get_interview_report_repository
from app.repositories.coding_interview_repository import CodingInterviewRepository
from app.repositories.interview_report_repository import InterviewReportRepository
from app.repositories.interview_repository import InterviewRepository
from app.services.session_management_service import SessionManagementService


def get_session_management_service(
    interview_repository: InterviewRepository = Depends(get_interview_repository),
    coding_repository: CodingInterviewRepository = Depends(get_coding_repository),
    report_repository: InterviewReportRepository = Depends(get_interview_report_repository),
) -> SessionManagementService:
    return SessionManagementService(
        interview_repository=interview_repository,
        coding_repository=coding_repository,
        report_repository=report_repository,
    )


__all__ = [
    "get_database",
    "get_gemini_client",
    "get_session_management_service",
]
