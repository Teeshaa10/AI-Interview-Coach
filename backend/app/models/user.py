from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


class UserInDB(BaseModel):
    """
    Represents a user exactly as it's stored in, and read from, MongoDB.

    This is a deliberately different class from the request/response
    schemas in app/schemas/user.py. The API layer should never see
    hashed_password, and the database layer shouldn't have to know about
    API-only concerns like which fields are required on a registration
    form. Keeping them separate means a change to the API response shape
    can never accidentally leak a new database field, and a change to how
    we store users can never silently break the API contract.

    id is a plain string, never Mongo's ObjectId — see user_repository.py
    for where that conversion happens. Nothing outside the repository
    layer should ever import bson.ObjectId.
    """

    id: str
    email: EmailStr
    hashed_password: str
    full_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
