from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.interview_dependencies import get_interview_service
from app.models.user import UserInDB
from app.schemas.interview import InterviewQuestionRequest, InterviewQuestionsResponse
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post(
    "/questions",
    response_model=InterviewQuestionsResponse,
    summary="Generate resume-based interview questions",
    description=(
        "Retrieves the authenticated user's most relevant resume chunks with semantic "
        "search and uses Gemini to create a structured, role-specific interview set."
    ),
)
async def generate_interview_questions(
    payload: InterviewQuestionRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    service: Annotated[InterviewService, Depends(get_interview_service)],
) -> InterviewQuestionsResponse:
    return await service.generate_questions(
        user_id=current_user.id,
        request=payload,
    )
