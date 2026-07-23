from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.interview_report import InterviewReport


class InterviewReportRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["interview_reports"]

    async def create(self, report: InterviewReport) -> str:
        document = report.model_dump(exclude={"id"}, mode="python")
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_by_id(self, report_id: str) -> InterviewReport | None:
        if not ObjectId.is_valid(report_id):
            return None
        document = await self.collection.find_one({"_id": ObjectId(report_id)})
        return self._to_schema(document)

    async def get_by_interview_id(self, interview_id: str) -> InterviewReport | None:
        document = await self.collection.find_one({"interview_id": interview_id})
        return self._to_schema(document)

    async def replace_for_interview(self, report: InterviewReport) -> str:
        document = report.model_dump(exclude={"id"}, mode="python")
        result = await self.collection.find_one_and_replace(
            {"interview_id": report.interview_id, "user_id": report.user_id},
            document,
            upsert=True,
            return_document=True,
        )
        if result and "_id" in result:
            return str(result["_id"])
        saved = await self.collection.find_one({"interview_id": report.interview_id, "user_id": report.user_id})
        return str(saved["_id"])

    async def delete(self, report_id: str, user_id: str) -> bool:
        if not ObjectId.is_valid(report_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(report_id), "user_id": user_id})
        return result.deleted_count == 1

    async def list_user_reports(self, user_id: str, page: int, limit: int) -> tuple[list[InterviewReport], int]:
        query = {"user_id": user_id}
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)
        reports = []
        async for document in cursor:
            report = self._to_schema(document)
            if report:
                reports.append(report)
        return reports, total

    async def list_all_user_reports(self, user_id: str) -> list[InterviewReport]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", 1)
        reports = []
        async for document in cursor:
            report = self._to_schema(document)
            if report:
                reports.append(report)
        return reports

    @staticmethod
    def _to_schema(document: dict | None) -> InterviewReport | None:
        if document is None:
            return None
        document = dict(document)
        document["id"] = str(document.pop("_id"))
        return InterviewReport.model_validate(document)
