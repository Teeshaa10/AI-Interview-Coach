from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.coding_interview import CodingInterviewSession, CodingSubmission


class CodingInterviewRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.sessions = database["coding_interviews"]
        self.submissions = database["coding_submissions"]

    async def create_session(self, session: CodingInterviewSession) -> str:
        result = await self.sessions.insert_one(session.model_dump(exclude={"id"}, mode="python"))
        return str(result.inserted_id)

    async def get_session(self, session_id: str) -> CodingInterviewSession | None:
        if not ObjectId.is_valid(session_id):
            return None
        document = await self.sessions.find_one({"_id": ObjectId(session_id)})
        if document is None:
            return None
        document["id"] = str(document.pop("_id"))
        return CodingInterviewSession.model_validate(document)

    async def create_submission(self, submission: CodingSubmission) -> str:
        result = await self.submissions.insert_one(submission.model_dump(exclude={"id"}, mode="python"))
        return str(result.inserted_id)

    async def get_submissions(self, session_id: str, user_id: str) -> list[CodingSubmission]:
        cursor = self.submissions.find({"session_id": session_id, "user_id": user_id}).sort("created_at", 1)
        result = []
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            result.append(CodingSubmission.model_validate(document))
        return result

    async def complete_session(self, session_id: str, final_score: float) -> None:
        await self.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"completed": True, "final_score": final_score, "completed_at": datetime.utcnow()}},
        )

    async def list_user_sessions(self, user_id: str, page: int, limit: int) -> tuple[list[CodingInterviewSession], int]:
        query = {"user_id": user_id}
        total = await self.sessions.count_documents(query)
        cursor = self.sessions.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)
        sessions = []
        async for document in cursor:
            document["id"] = str(document.pop("_id"))
            sessions.append(CodingInterviewSession.model_validate(document))
        return sessions, total
