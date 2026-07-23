from pathlib import Path
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.embedding_dependencies import get_semantic_search_service
from app.repositories.resume_repository import ResumeRepository
from app.services.resume_service import ResumeService
from app.services.semantic_search_service import SemanticSearchService

BACKEND_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIRECTORY = BACKEND_ROOT / "uploads"


def get_resume_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> ResumeRepository:
    return ResumeRepository(database)


def get_resume_service(
    repository: Annotated[ResumeRepository, Depends(get_resume_repository)],
    semantic_search_service: Annotated[
        SemanticSearchService,
        Depends(get_semantic_search_service),
    ],
) -> ResumeService:
    return ResumeService(
        repository=repository,
        upload_directory=UPLOAD_DIRECTORY,
        semantic_search_service=semantic_search_service,
    )
