import logging
from datetime import datetime
from typing import Any, Mapping

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from app.models.resume import Resume

logger = logging.getLogger(__name__)


class ResumeRepository:
    """
    MongoDB data-access layer for resume documents.

    MongoDB-specific details remain here so services can work with domain
    objects rather than raw BSON dictionaries.
    """

    COLLECTION_NAME = "resumes"

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[self.COLLECTION_NAME]

    async def ensure_indexes(self) -> None:
        """Create the index used to retrieve a user's latest resume."""

        await self._collection.create_index(
            [("user_id", 1), ("created_at", DESCENDING)],
            name="user_resume_created_at_idx",
        )

    async def create_resume(
        self,
        *,
        user_id: str,
        filename: str,
        original_filename: str,
        file_type: str,
        file_path: str,
        extracted_text: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> Resume:
        """Insert a resume document and return its domain representation."""

        document: dict[str, Any] = {
            "user_id": user_id,
            "filename": filename,
            "original_filename": original_filename,
            "file_type": file_type,
            "file_path": file_path,
            "extracted_text": extracted_text,
            "created_at": created_at,
            "updated_at": updated_at,
        }

        try:
            result = await self._collection.insert_one(document)
        except PyMongoError:
            logger.exception(
                "Failed to create resume",
                extra={"user_id": user_id},
            )
            raise

        document["_id"] = result.inserted_id
        return self._to_model(document)

    async def get_resume_by_user(self, user_id: str) -> Resume | None:
        """Return the user's most recently uploaded resume."""

        document = await self._collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", DESCENDING)],
        )

        return self._to_model(document) if document else None

    async def get_resume_by_id(self, resume_id: str) -> Resume | None:
        """Return a resume by ID, treating invalid ObjectIds as not found."""

        if not ObjectId.is_valid(resume_id):
            return None

        document = await self._collection.find_one(
            {"_id": ObjectId(resume_id)}
        )

        return self._to_model(document) if document else None

    async def delete_resume(self, resume_id: str) -> bool:
        """Delete a resume document and report whether it existed."""

        if not ObjectId.is_valid(resume_id):
            return False

        result = await self._collection.delete_one(
            {"_id": ObjectId(resume_id)}
        )

        return result.deleted_count == 1

    @staticmethod
    def _to_model(document: Mapping[str, Any]) -> Resume:
        """Convert a MongoDB document into the Resume domain model."""

        return Resume(
            id=str(document["_id"]),
            user_id=str(document["user_id"]),
            filename=str(document["filename"]),
            original_filename=str(document["original_filename"]),
            file_type=str(document["file_type"]),
            file_path=str(document["file_path"]),
            extracted_text=str(document["extracted_text"]),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )
