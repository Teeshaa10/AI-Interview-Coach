from pathlib import Path
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

# from app.db.mongodb import get_database
from app.db.mongo import get_database
from app.repositories.resume_repository import ResumeRepository
from app.services.resume_service import ResumeService

# backend/uploads, assuming this file is backend/app/resume_dependencies.py
BACKEND_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIRECTORY = BACKEND_ROOT / "uploads"


def get_resume_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> ResumeRepository:
    """
    Construct the repository for the current request.

    FastAPI caches dependencies within a request, so downstream dependencies
    receive the same repository instance unless caching is explicitly disabled.
    """

    return ResumeRepository(database)


def get_resume_service(
    repository: Annotated[
        ResumeRepository,
        Depends(get_resume_repository),
    ],
) -> ResumeService:
    """Construct ResumeService with its repository and upload directory."""

    return ResumeService(
        repository=repository,
        upload_directory=UPLOAD_DIRECTORY,
    )
