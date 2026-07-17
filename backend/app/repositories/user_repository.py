import logging
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import UserInDB

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "users"


class UserRepository:
    """
    Owns every query the app runs against the `users` collection.

    Services call methods on this class — get_by_email, create — instead
    of touching `db.users` directly. That boundary is what makes
    AuthService unit-testable with a fake repository and no real MongoDB
    connection, and it means if the users collection's shape ever changes,
    exactly one file needs to change.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db[_COLLECTION_NAME]

    async def create_indexes(self) -> None:
        """
        Creates a unique index on email.

        The service layer already checks "does this email exist?" before
        inserting, but that check-then-insert has a race condition: two
        registration requests for the same email arriving within
        milliseconds of each other could both pass the check before either
        insert completes. A unique index is the database-level guarantee
        that closes that gap — MongoDB itself will reject the second
        insert, no matter how the application-level timing works out.
        """
        await self._collection.create_index("email", unique=True)

    async def get_by_email(self, email: str) -> UserInDB | None:
        document = await self._collection.find_one({"email": email})
        return self._to_model(document) if document else None

    async def get_by_id(self, user_id: str) -> UserInDB | None:
        if not ObjectId.is_valid(user_id):
            return None
        document = await self._collection.find_one({"_id": ObjectId(user_id)})
        return self._to_model(document) if document else None

    async def create(self, email: str, hashed_password: str, full_name: str) -> UserInDB:
        document = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return self._to_model(document)

    @staticmethod
    def _to_model(document: dict) -> UserInDB:
        """
        Converts a raw MongoDB document into a UserInDB.

        This is the one place in the entire app that touches an ObjectId —
        it's translated into a plain string here and never leaves this
        function as anything else. Every other layer (services, schemas,
        JWT payloads) works with plain string ids, which keeps a
        MongoDB-specific detail from leaking into code that shouldn't need
        to know it exists.
        """
        document = dict(document)
        document["id"] = str(document.pop("_id"))
        return UserInDB(**document)
