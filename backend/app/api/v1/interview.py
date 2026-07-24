from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.interview_dependencies import (
    get_evaluation_service,
    get_interview_repository,
    get_interview_service,
)
from app.models.user import UserInDB
from app.repositories.interview_repository import InterviewRepository
from app.schemas.interview import InterviewQuestionRequest
from app.schemas.interview_evaluation import InterviewEvaluationResponse
from app.schemas.interview_session import (
    FinishInterviewResponse,
    InterviewHistoryItem,
    InterviewHistoryResponse,
    InterviewQuestion,
    InterviewSession,
    InterviewSessionCreate,
    InterviewSessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.services.evaluation_service import EvaluationService
from app.services.interview_service import InterviewService

router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)


@router.post(
    "/start",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_interview(
    request: InterviewSessionCreate,
    current_user: UserInDB = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service),
    repository: InterviewRepository = Depends(get_interview_repository),
):
    generated = await interview_service.generate_questions(
        user_id=current_user.id,
        request=InterviewQuestionRequest(
            resume_id=request.resume_id,
            job_role=request.job_role,
            experience_level=request.experience_level,
            number_of_questions=request.number_of_questions,
        ),
    )

    questions = []

    number = 1

    for q in generated.technical_questions:
        questions.append(
            InterviewQuestion(
                question_number=number,
                question=q,
                category="Technical",
            )
        )
        number += 1

    for q in generated.project_questions:
        questions.append(
            InterviewQuestion(
                question_number=number,
                question=q,
                category="Project",
            )
        )
        number += 1

    for q in generated.hr_questions:
        questions.append(
            InterviewQuestion(
                question_number=number,
                question=q,
                category="HR",
            )
        )
        number += 1

    for q in generated.coding_questions:
        questions.append(
            InterviewQuestion(
                question_number=number,
                question=q,
                category="Coding",
            )
        )
        number += 1

    interview = InterviewSession(
        user_id=current_user.id,
        resume_id=request.resume_id,
        job_role=request.job_role,
        experience_level=request.experience_level,
        questions=questions,
        mode=request.mode,
    )

    interview_id = await repository.create_interview(interview)

    return InterviewSessionResponse(
        interview_id=interview_id,
        questions=questions,
    )


@router.post(
    "/{interview_id}/answer",
    response_model=SubmitAnswerResponse,
)
async def submit_answer(
    interview_id: str,
    request: SubmitAnswerRequest,
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewRepository = Depends(get_interview_repository),
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
):
    interview = await repository.get_interview_by_id(interview_id)

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    if interview.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    if request.question_number < 1 or request.question_number > len(interview.questions):
        raise HTTPException(
            status_code=400,
            detail="Invalid question number",
        )

    question = interview.questions[request.question_number - 1]

    evaluation: InterviewEvaluationResponse = (
        await evaluation_service.evaluate_answer(
            question=question.question,
            answer=request.answer,
            resume_context="",
            job_role=interview.job_role,
            experience_level=interview.experience_level,
        )
    )

    question.answer = request.answer
    question.technical_score = evaluation.technical_score
    question.communication_score = evaluation.communication_score
    question.completeness_score = evaluation.completeness_score
    question.overall_score = evaluation.overall_score
    question.strengths = evaluation.strengths
    question.weaknesses = evaluation.weaknesses
    question.better_answer = evaluation.better_answer
    question.feedback = evaluation.feedback

    await repository.update_question(
        interview_id,
        request.question_number,
        question.model_dump(),
    )

    return SubmitAnswerResponse(
        question=question,
    )


@router.post(
    "/{interview_id}/finish",
    response_model=FinishInterviewResponse,
)
async def finish_interview(
    interview_id: str,
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewRepository = Depends(get_interview_repository),
):
    interview = await repository.get_interview_by_id(interview_id)

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    if interview.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    scores = [
        q.overall_score
        for q in interview.questions
        if q.overall_score is not None
    ]

    average = (
        round(sum(scores) / len(scores), 2)
        if scores
        else 0.0
    )

    await repository.mark_completed(
        interview_id,
        average,
    )

    return FinishInterviewResponse(
        interview_id=interview_id,
        average_score=average,
        completed=True,
    )


@router.get(
    "/history",
    response_model=InterviewHistoryResponse,
)
async def interview_history(
    current_user: UserInDB = Depends(get_current_user),
    repository: InterviewRepository = Depends(get_interview_repository),
):
    interviews = await repository.get_user_interviews(
        current_user.id,
    )

    return InterviewHistoryResponse(
        interviews=[
            InterviewHistoryItem(
                interview_id=i.id,
                job_role=i.job_role,
                experience_level=i.experience_level,
                average_score=i.average_score,
                completed=i.completed,
                created_at=i.created_at,
                mode=i.mode,
            )
            for i in interviews
        ]
    )