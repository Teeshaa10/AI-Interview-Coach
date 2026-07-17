from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """
    What a client must send to POST /api/v1/auth/register.

    EmailStr (from pydantic) validates the email format at the schema
    level, before any route or service code runs — an invalid email never
    even reaches our business logic. Field(min_length=8) on the password
    is a first line of defense; the field_validator below adds the
    complexity rule that a plain Field constraint can't express.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def password_must_be_reasonably_strong(cls, value: str) -> str:
        """Requires at least one letter and one digit. This is a floor,
        not a full policy — it catches "password" and "12345678" without
        being so strict it frustrates real users. Pydantic runs this
        automatically on every request; a route never has to remember to
        call it."""
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        return value


class UserLoginRequest(BaseModel):
    """What a client sends to POST /api/v1/auth/login. Deliberately no
    complexity validation here — login should reject bad credentials with
    a generic error, not reveal password policy details to someone probing
    the endpoint."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    The public shape of a user, returned by /register, /login, and /me.

    Notice hashed_password never appears here — this class defines what
    the API is allowed to expose, independent of what UserInDB stores.
    Even if a route accidentally passed a full UserInDB object where a
    UserResponse is expected, FastAPI's response_model filtering strips
    every field this class doesn't declare.
    """

    id: str
    email: EmailStr
    full_name: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Returned by /login — the JWT plus the user it belongs to, so the
    frontend can populate its auth state from a single response instead of
    making a second /me call immediately after logging in."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
