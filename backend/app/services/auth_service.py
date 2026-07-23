import logging

from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.auth_exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.models.user import UserInDB
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """
    Owns registration and login business logic.

    Routes in app/api/v1/auth.py stay thin: they parse the HTTP request
    into a schema and call a method here. Every actual decision — does
    this email already exist, does this password match — lives in this
    class. That's what makes it testable independent of FastAPI: a unit
    test can call AuthService(fake_repository).register(...) directly,
    with no HTTP layer, no running server, and no real database involved.
    """

    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    async def register(self, email: str, password: str, full_name: str) -> UserInDB:
        """Creates a new user, or raises UserAlreadyExistsError if the
        email is already taken. The password is hashed here — the plain
        password is never passed to the repository and never reaches the
        database in any form."""
        existing_user = await self._users.get_by_email(email)
        if existing_user is not None:
            logger.warning(f"Registration attempted with existing email: {email}")
            raise UserAlreadyExistsError(email)

        hashed_password = hash_password(password)
        user = await self._users.create(
            email=email, hashed_password=hashed_password, full_name=full_name
        )
        logger.info(f"New user registered: {user.id}")
        return user

    async def login(self, email: str, password: str) -> tuple[UserInDB, str]:
        """
        Verifies credentials and, on success, returns the user and a fresh
        JWT. Raises InvalidCredentialsError for both "no such user" and
        "wrong password" — see the exception's docstring for why that
        distinction is deliberately hidden from the caller.
        """
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {email}")
            raise InvalidCredentialsError()

        token = create_access_token(subject=user.id)
        logger.info(f"User logged in: {user.id}")
        return user, token
