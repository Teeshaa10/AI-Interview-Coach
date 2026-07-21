import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.auth_exceptions import (
    AuthError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.exceptions.evaluation import EvaluationError
from app.exceptions.interview import InterviewError
from app.exceptions.resume import ResumeError
from app.exceptions.voice import VoiceError

logger = logging.getLogger(__name__)

_STATUS_CODE_MAP: dict[type[AuthError], int] = {
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthError)
    async def handle_auth_error(
        request: Request,
        exc: AuthError,
    ) -> JSONResponse:
        status_code = _STATUS_CODE_MAP.get(
            type(exc),
            status.HTTP_400_BAD_REQUEST,
        )

        logger.info(
            "Handled %s on %s: %s",
            type(exc).__name__,
            request.url.path,
            exc,
        )

        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ResumeError)
    async def handle_resume_error(
        request: Request,
        exc: ResumeError,
    ) -> JSONResponse:
        logger.info(
            "Handled %s on %s: %s",
            type(exc).__name__,
            request.url.path,
            exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(InterviewError)
    async def handle_interview_error(
        request: Request,
        exc: InterviewError,
    ) -> JSONResponse:
        logger.info(
            "Handled %s on %s: %s",
            type(exc).__name__,
            request.url.path,
            exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(EvaluationError)
    async def handle_evaluation_error(
        request: Request,
        exc: EvaluationError,
    ) -> JSONResponse:
        logger.info(
            "Handled %s on %s: %s",
            type(exc).__name__,
            request.url.path,
            exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(VoiceError)
    async def handle_voice_error(
        request: Request,
        exc: VoiceError,
    ) -> JSONResponse:
        logger.info(
            "Handled %s on %s: %s",
            type(exc).__name__,
            request.url.path,
            exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )