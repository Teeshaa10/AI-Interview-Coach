from fastapi import APIRouter, Depends, Query, status

from app.coding_dependencies import (
    get_code_execution_service,
    get_coding_interview_service,
    get_coding_repository,
)
from app.dependencies import get_current_user
from app.exceptions.coding import (
    CodingSessionCompletedError,
    CodingSessionNotFoundError,
    ForbiddenCodingAccessError,
)
from app.models.user import UserInDB
from app.repositories.coding_interview_repository import CodingInterviewRepository
from app.schemas.coding_interview import (
    CodingHistoryResponse,
    CodingInterviewResponse,
    CodingInterviewSession,
    CodingInterviewStartRequest,
    CodingQuestionPublic,
    CodingRunRequest,
    CodingRunResponse,
    CodingSubmission,
    CodingSubmitRequest,
    CodingSubmitResponse,
    SupportedLanguagesResponse,
)
from app.services.code_execution_service import CodeExecutionService
from app.services.coding_interview_service import CodingInterviewService

router = APIRouter(prefix="/coding-interviews", tags=["Coding Interview"])


def _public_question(question) -> CodingQuestionPublic:
    return CodingQuestionPublic.model_validate(question.model_dump(exclude={"hidden_test_cases"}))


def _response(session: CodingInterviewSession) -> CodingInterviewResponse:
    return CodingInterviewResponse(
        session_id=session.id or "",
        role=session.role,
        difficulty=session.difficulty,
        language=session.language,
        questions=[_public_question(q) for q in session.questions],
        completed=session.completed,
        final_score=session.final_score,
    )


def _owned(session: CodingInterviewSession | None, user_id: str) -> CodingInterviewSession:
    if session is None:
        raise CodingSessionNotFoundError()
    if session.user_id != user_id:
        raise ForbiddenCodingAccessError()
    return session


@router.post("/start", response_model=CodingInterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_coding_interview(
    request: CodingInterviewStartRequest,
    current_user: UserInDB = Depends(get_current_user),
    service: CodingInterviewService = Depends(get_coding_interview_service),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
):
    questions = await service.generate_questions(request)
    session = CodingInterviewSession(
        user_id=current_user.id,
        resume_id=request.resume_id,
        role=request.role,
        experience_level=request.experience_level,
        difficulty=request.difficulty,
        language=request.language.lower(),
        questions=questions,
    )
    session.id = await repository.create_session(session)
    return _response(session)


@router.get("/history", response_model=CodingHistoryResponse)
async def coding_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
):
    sessions, total = await repository.list_user_sessions(current_user.id, page, limit)
    return CodingHistoryResponse(sessions=[_response(s) for s in sessions], page=page, limit=limit, total=total)


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def supported_languages(
    current_user: UserInDB = Depends(get_current_user),
    execution_service: CodeExecutionService = Depends(get_code_execution_service),
):
    return SupportedLanguagesResponse(provider=execution_service.provider_name, languages=execution_service.supported_languages)


@router.get("/{session_id}", response_model=CodingInterviewResponse)
async def get_coding_interview(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
):
    return _response(_owned(await repository.get_session(session_id), current_user.id))


@router.post("/{session_id}/run", response_model=CodingRunResponse)
async def run_code(
    session_id: str,
    request: CodingRunRequest,
    current_user: UserInDB = Depends(get_current_user),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
    service: CodingInterviewService = Depends(get_coding_interview_service),
):
    session = _owned(await repository.get_session(session_id), current_user.id)
    if session.completed:
        raise CodingSessionCompletedError()
    return await service.run_code(session=session, request=request)


@router.post("/{session_id}/submit", response_model=CodingSubmitResponse)
async def submit_code(
    session_id: str,
    request: CodingSubmitRequest,
    current_user: UserInDB = Depends(get_current_user),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
    service: CodingInterviewService = Depends(get_coding_interview_service),
):
    session = _owned(await repository.get_session(session_id), current_user.id)
    if session.completed:
        raise CodingSessionCompletedError()
    submission = await service.submit(session=session, request=request, user_id=current_user.id)
    next_question = next((q for q in session.questions if q.question_number > request.question_number), None)
    return CodingSubmitResponse(submission=submission, next_question=_public_question(next_question) if next_question else None)


@router.post("/{session_id}/complete", response_model=CodingInterviewResponse)
async def complete_coding_interview(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
):
    session = _owned(await repository.get_session(session_id), current_user.id)
    if session.completed:
        raise CodingSessionCompletedError()
    submissions = await repository.get_submissions(session_id, current_user.id)
    latest_by_question = {}
    for submission in submissions:
        latest_by_question[submission.question_number] = submission
    scores = [item.overall_score for item in latest_by_question.values()]
    final_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    await repository.complete_session(session_id, final_score)
    session.completed = True
    session.final_score = final_score
    return _response(session)


@router.get("/{session_id}/submissions", response_model=list[CodingSubmission])
async def get_submissions(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: CodingInterviewRepository = Depends(get_coding_repository),
):
    _owned(await repository.get_session(session_id), current_user.id)
    return await repository.get_submissions(session_id, current_user.id)
