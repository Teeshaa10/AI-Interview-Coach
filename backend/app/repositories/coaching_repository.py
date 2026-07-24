from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.coaching import PracticePlan


class CoachingRepository:
    """Persists Module 9 practice plans. Follows the same
    find/insert/update pattern as CodingInterviewRepository."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.plans = database["coaching_plans"]

    async def create_plan(self, plan: PracticePlan) -> str:
        result = await self.plans.insert_one(plan.model_dump(exclude={"id"}, mode="python"))
        return str(result.inserted_id)

    async def get_plan(self, plan_id: str) -> PracticePlan | None:
        if not ObjectId.is_valid(plan_id):
            return None
        document = await self.plans.find_one({"_id": ObjectId(plan_id)})
        if document is None:
            return None
        document["id"] = str(document.pop("_id"))
        return PracticePlan.model_validate(document)

    async def get_active_plan(self, user_id: str) -> PracticePlan | None:
        document = await self.plans.find_one(
            {"user_id": user_id, "is_active": True},
            sort=[("created_at", -1)],
        )
        if document is None:
            return None
        document["id"] = str(document.pop("_id"))
        return PracticePlan.model_validate(document)

    async def deactivate_all_plans(self, user_id: str) -> None:
        await self.plans.update_many({"user_id": user_id, "is_active": True}, {"$set": {"is_active": False}})

    async def set_item_completion(self, plan_id: str, user_id: str, item_id: str, completed: bool) -> bool:
        if not ObjectId.is_valid(plan_id):
            return False
        result = await self.plans.update_one(
            {"_id": ObjectId(plan_id), "user_id": user_id, "items.item_id": item_id},
            {"$set": {"items.$.completed": completed}},
        )
        return result.matched_count == 1
