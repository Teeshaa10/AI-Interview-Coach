from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.voice import VoiceAudioRecord


class VoiceRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["voice_audio"]

    async def create_audio_record(self, record: VoiceAudioRecord) -> str:
        document = record.model_dump(exclude={"id"}, mode="python")
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_audio_record(self, audio_id: str) -> Optional[VoiceAudioRecord]:
        if not ObjectId.is_valid(audio_id):
            return None

        document = await self.collection.find_one({"_id": ObjectId(audio_id)})
        if document is None:
            return None

        document["id"] = str(document.pop("_id"))
        return VoiceAudioRecord.model_validate(document)
