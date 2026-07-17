"""
Central place for FastAPI dependency functions.

FastAPI's Depends() system is how we do dependency injection: a route
declares what it needs (a database, the current settings, the logged-in
user) as a function parameter, and FastAPI calls the matching provider
function to supply it. Collecting those provider functions here — rather
than importing them from app.db.mongo, app.repositories.user_repository,
etc. separately all over the codebase — gives every route one consistent
import path, and gives us a single place to swap in fakes when we start
writing tests.

Module 1 adds get_user_repository, get_auth_service, and get_current_user,
exactly the growth this file's Module 0 docstring anticipated.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.chroma import get_chroma_client
from app.db.mongo import get_database
from app.models.user import UserInDB
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

# HTTPBearer, not OAuth2PasswordBearer: our /auth/login endpoint accepts a
# JSON body (UserLoginRequest), not the OAuth2 spec's form-encoded
# username/password. HTTPBearer only does the one thing we need — read the
# "Authorization: Bearer <token>" header — without implying a form-based
# login flow that Swagger UI would otherwise try, and fail, to drive.
_bearer_scheme = HTTPBearer()


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserRepository:
    """Constructs a UserRepository bound to the current request's database
    handle. Instantiating it per request is cheap — it only wraps a
    collection reference — and keeps the repository itself stateless."""
    return UserRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Constructs an AuthService with its repository dependency already
    injected. This is FastAPI building the object graph per request: routes
    ask for an AuthService and never see the UserRepository underneath it."""
    return AuthService(user_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserInDB:
    """
    The auth guard for protected routes.

    A route that requires login declares
    `current_user: UserInDB = Depends(get_current_user)` and FastAPI
    handles the rest: extracting the Authorization header, verifying the
    JWT, loading the user from MongoDB, and rejecting the request with 401
    before the route's own body ever runs if any step fails. This is the
    dependency /me (in app/api/v1/auth.py) uses, and every protected route
    in future modules will use the same one.
    """
    try:
        user_id = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


__all__ = [
    "Settings",
    "get_settings",
    "get_database",
    "get_chroma_client",
    "get_user_repository",
    "get_auth_service",
    "get_current_user",
]
