import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.resume import ResumeError

from app.exceptions.auth_exceptions import (
    AuthError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)

_STATUS_CODE_MAP: dict[type[AuthError], int] = {
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
}


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers one handler that catches AuthError and every subclass of it,
    converting each into a JSON response with the correct status code.

    Without this, a raised UserAlreadyExistsError would bubble up as
    FastAPI's generic unhandled-exception 500 response — the caller would
    see "Internal Server Error" instead of "email already taken," and we'd
    lose the distinction entirely. This handler is the only place in the
    app that translates a domain error into an HTTP status code, which
    means services and repositories can raise plain, meaningful Python
    exceptions without importing anything from fastapi or knowing what
    status code they should produce.

    _STATUS_CODE_MAP is a dict, not an if/elif chain, so adding a new auth
    exception later is a one-line addition here, not a new branch.
    """

    @app.exception_handler(AuthError)
    async def handle_auth_error(request: Request, exc: AuthError) -> JSONResponse:
        status_code = _STATUS_CODE_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        logger.info(f"Handled {type(exc).__name__} on {request.url.path}: {exc}")
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.exception_handler(ResumeError)
    async def handle_resume_error(request: Request, exc: ResumeError) -> JSONResponse:
        logger.info("Handled %s on %s: %s", type(exc).__name__, request.url.path, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
