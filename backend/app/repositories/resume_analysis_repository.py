from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class ResumeAnalysisRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["resume_analyses"]

    async def create(self, analysis_data: dict) -> dict:
        analysis_data["created_at"] = datetime.now(timezone.utc)

        result = await self.collection.insert_one(analysis_data)

        created_analysis = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        return self._serialize(created_analysis)

    async def get_by_id(self, analysis_id: str, user_id: str) -> dict | None:
        if not ObjectId.is_valid(analysis_id):
            return None

        analysis = await self.collection.find_one(
            {
                "_id": ObjectId(analysis_id),
                "user_id": user_id,
            }
        )

        return self._serialize(analysis) if analysis else None

    async def get_latest_by_resume(
        self,
        resume_id: str,
        user_id: str,
    ) -> dict | None:
        analysis = await self.collection.find_one(
            {
                "resume_id": resume_id,
                "user_id": user_id,
            },
            sort=[("created_at", -1)],
        )

        return self._serialize(analysis) if analysis else None

    async def get_history(self, user_id: str) -> list[dict]:
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1)

        analyses = await cursor.to_list(length=None)

        return [self._serialize(analysis) for analysis in analyses]

    async def delete(self, analysis_id: str, user_id: str) -> bool:
        if not ObjectId.is_valid(analysis_id):
            return False

        result = await self.collection.delete_one(
            {
                "_id": ObjectId(analysis_id),
                "user_id": user_id,
            }
        )

        return result.deleted_count == 1

    @staticmethod
    def _serialize(document: dict | None) -> dict | None:
        if not document:
            return None

        serialized = dict(document)
        serialized["id"] = str(serialized.pop("_id"))

        return serialized