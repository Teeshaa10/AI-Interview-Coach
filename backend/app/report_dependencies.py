from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.interview_dependencies import get_interview_repository
from app.repositories.interview_report_repository import InterviewReportRepository
from app.repositories.interview_repository import InterviewRepository
from app.services.interview_report_service import InterviewReportService


def get_interview_report_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> InterviewReportRepository:
    return InterviewReportRepository(db)


def get_interview_report_service(
    interview_repository: InterviewRepository = Depends(get_interview_repository),
    report_repository: InterviewReportRepository = Depends(get_interview_report_repository),
) -> InterviewReportService:
    return InterviewReportService(interview_repository, report_repository)
