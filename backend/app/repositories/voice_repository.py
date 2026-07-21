from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class VoiceRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["voice_audio"]

    async def create_audio_record(
        self,
        user_id: str,
        filename: str,
        stored_filename: str,
        content_type: str,
        file_path: str,
        voice: str,
        text_length: int,
    ) -> dict:
        document = {
            "user_id": user_id,
            "filename": filename,
            "stored_filename": stored_filename,
            "content_type": content_type,
            "file_path": file_path,
            "voice": voice,
            "text_length": text_length,
            "created_at": datetime.now(timezone.utc),
        }

        result = await self.collection.insert_one(document)

        created_record = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        return self._serialize(created_record)

    async def get_audio_by_id(
        self,
        audio_id: str,
    ) -> dict | None:
        if not ObjectId.is_valid(audio_id):
            return None

        document = await self.collection.find_one(
            {"_id": ObjectId(audio_id)}
        )

        return self._serialize(document) if document else None

    async def get_user_audio(
        self,
        audio_id: str,
        user_id: str,
    ) -> dict | None:
        if not ObjectId.is_valid(audio_id):
            return None

        document = await self.collection.find_one(
            {
                "_id": ObjectId(audio_id),
                "user_id": user_id,
            }
        )

        return self._serialize(document) if document else None

    async def delete_audio_record(
        self,
        audio_id: str,
        user_id: str,
    ) -> bool:
        if not ObjectId.is_valid(audio_id):
            return False

        result = await self.collection.delete_one(
            {
                "_id": ObjectId(audio_id),
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