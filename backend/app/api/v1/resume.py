from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.dependencies import get_current_user
from app.resume_dependencies import get_resume_service
from app.schemas.resume import (
    DeleteResumeResponse,
    ResumeResponse,
    UploadResponse,
)
from app.services.resume_service import ResumeService

router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


def _extract_user_id(current_user: Any) -> str:
    """
    Normalize the authenticated user's ID.

    Existing authentication implementations commonly return a Pydantic model,
    a domain object, or a MongoDB dictionary. Supporting all three keeps the
    resume module easy to integrate without weakening authentication.
    """

    if isinstance(current_user, dict):
        value = current_user.get("id") or current_user.get("_id")
    else:
        value = getattr(current_user, "id", None) or getattr(
            current_user,
            "_id",
            None,
        )

    if value is None:
        raise RuntimeError(
            "get_current_user must return an object containing id or _id"
        )

    return str(value)


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a resume",
)
async def upload_resume(
    file: Annotated[
        UploadFile,
        File(description="A PDF or DOCX resume, maximum size 10 MB"),
    ],
    current_user: Annotated[Any, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> UploadResponse:
    """
    Upload a resume for the authenticated user.

    The route performs HTTP input/output orchestration only. Validation,
    storage, parsing, and persistence are delegated to ResumeService.
    """

    resume = await service.upload_resume(
        user_id=_extract_user_id(current_user),
        upload_file=file,
    )

    return UploadResponse(
        resume=ResumeResponse.model_validate(resume)
    )


@router.get(
    "/me",
    response_model=ResumeResponse,
    summary="Get my latest resume",
)
async def get_my_resume(
    current_user: Annotated[Any, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> ResumeResponse:
    """Return the latest resume belonging to the authenticated user."""

    resume = await service.get_resume_for_user(
        user_id=_extract_user_id(current_user)
    )

    return ResumeResponse.model_validate(resume)


@router.delete(
    "/{resume_id}",
    response_model=DeleteResumeResponse,
    summary="Delete a resume",
)
async def delete_resume(
    resume_id: str,
    current_user: Annotated[Any, Depends(get_current_user)],
    service: Annotated[ResumeService, Depends(get_resume_service)],
) -> DeleteResumeResponse:
    """Delete a resume owned by the authenticated user."""

    await service.delete_resume(
        resume_id=resume_id,
        user_id=_extract_user_id(current_user),
    )

    return DeleteResumeResponse()
