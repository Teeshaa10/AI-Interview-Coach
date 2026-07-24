from datetime import datetime
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.interview_session import InterviewSession


class InterviewRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["interview_sessions"]

    async def create_interview(
        self,
        interview: InterviewSession,
    ) -> str:
        document = interview.model_dump(
            exclude={"id"},
            mode="python",
        )

        result = await self.collection.insert_one(document)

        return str(result.inserted_id)

    async def get_interview_by_id(
        self,
        interview_id: str,
    ) -> Optional[InterviewSession]:

        document = await self.collection.find_one(
            {"_id": ObjectId(interview_id)}
        )

        if document is None:
            return None

        document["id"] = str(document.pop("_id"))

        return InterviewSession.model_validate(document)

    async def update_interview(
        self,
        interview_id: str,
        interview: InterviewSession,
    ) -> None:

        update_data = interview.model_dump(
            exclude={"id"},
            mode="python",
        )

        await self.collection.update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": update_data,
            },
        )

    async def update_question(
        self,
        interview_id: str,
        question_number: int,
        question_data: dict,
    ) -> None:

        update_fields = {}

        for key, value in question_data.items():
            update_fields[
                f"questions.{question_number - 1}.{key}"
            ] = value

        await self.collection.update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": update_fields,
            },
        )

    async def mark_completed(
        self,
        interview_id: str,
        average_score: float,
    ) -> None:

        await self.collection.update_one(
            {"_id": ObjectId(interview_id)},
            {
                "$set": {
                    "completed": True,
                    "average_score": average_score,
                    "completed_at": datetime.utcnow(),
                }
            },
        )

    async def get_user_interviews(
        self,
        user_id: str,
    ) -> list[InterviewSession]:

        cursor = self.collection.find(
            {"user_id": user_id}
        )

        interviews = []

        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            interviews.append(
                InterviewSession.model_validate(document)
            )

        return interviews

    async def delete_interview(
        self,
        interview_id: str,
    ) -> None:

        await self.collection.delete_one(
            {"_id": ObjectId(interview_id)}
        )

    async def delete_owned_interview(
        self,
        interview_id: str,
        user_id: str,
    ) -> bool:
        """Ownership-checked delete used by the unified session management
        endpoints (Module 6/7). Returns False if not found or not owned,
        instead of silently deleting like delete_interview()."""

        if not ObjectId.is_valid(interview_id):
            return False

        result = await self.collection.delete_one(
            {"_id": ObjectId(interview_id), "user_id": user_id}
        )

        return result.deleted_count == 1

    async def set_favorite(self, interview_id: str, user_id: str, favorite: bool) -> bool:
        if not ObjectId.is_valid(interview_id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(interview_id), "user_id": user_id},
            {"$set": {"favorite": favorite}},
        )
        return result.matched_count == 1