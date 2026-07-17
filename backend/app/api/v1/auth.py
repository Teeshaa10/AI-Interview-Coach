import logging

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service, get_current_user
from app.models.user import UserInDB
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_response(user: UserInDB) -> UserResponse:
    """Small shared mapper so the register/login/me routes below build the
    same response shape the same way, instead of repeating the field list
    three times and risking them drifting apart."""
    return UserResponse(
        id=user.id, email=user.email, full_name=user.full_name, created_at=user.created_at
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Creates a new account. Input validation (email format, password
    length/complexity) already happened in UserRegisterRequest before this
    function body runs — FastAPI rejects a malformed request with a 422
    before it ever reaches this route. If the email is already taken,
    AuthService raises UserAlreadyExistsError, which the handler in
    app/exceptions/handlers.py converts into a 409 response — this route
    never needs a try/except for that case.
    """
    user = await auth_service.register(
        email=payload.email, password=payload.password, full_name=payload.full_name
    )
    return _to_user_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Verifies credentials and returns a JWT plus the user it belongs to.
    Wrong email or password both surface as the same 401 (see
    InvalidCredentialsError's docstring for why)."""
    user, access_token = await auth_service.login(email=payload.email, password=payload.password)
    return TokenResponse(access_token=access_token, user=_to_user_response(user))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInDB = Depends(get_current_user)) -> UserResponse:
    """
    The first protected route in the project. get_current_user (in
    app/dependencies.py) does all the work — validating the bearer token
    and loading the user — before this function body even executes. If
    that dependency raises, this line never runs at all.
    """
    return _to_user_response(current_user)
