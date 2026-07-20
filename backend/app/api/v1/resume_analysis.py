from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.resume_analysis_dependencies import (
    get_resume_analysis_service,
)
from app.schemas.resume_analysis import (
    DeleteResumeAnalysisResponse,
    ResumeAnalysisDocument,
    ResumeAnalysisHistoryResponse,
    ResumeAnalysisRequest,
)
from app.services.resume_analysis_service import ResumeAnalysisService

router = APIRouter(
    prefix="/resume-analysis",
    tags=["Resume Analysis"],
)


@router.post(
    "/analyze",
    response_model=ResumeAnalysisDocument,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    current_user=Depends(get_current_user),
    service: ResumeAnalysisService = Depends(
        get_resume_analysis_service
    ),
):
    try:
        return await service.analyze_resume(
            user_id=str(current_user.id),
            resume_id=request.resume_id,
            target_role=request.target_role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/history",
    response_model=ResumeAnalysisHistoryResponse,
)
async def get_history(
    current_user=Depends(get_current_user),
    service: ResumeAnalysisService = Depends(
        get_resume_analysis_service
    ),
):
    analyses = await service.get_history(
        user_id=str(current_user.id),
    )

    return {"analyses": analyses}


@router.get(
    "/latest/{resume_id}",
    response_model=ResumeAnalysisDocument,
)
async def get_latest_analysis(
    resume_id: str,
    current_user=Depends(get_current_user),
    service: ResumeAnalysisService = Depends(
        get_resume_analysis_service
    ),
):
    analysis = await service.get_latest_analysis(
        resume_id=resume_id,
        user_id=str(current_user.id),
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    return analysis


@router.get(
    "/{analysis_id}",
    response_model=ResumeAnalysisDocument,
)
async def get_analysis(
    analysis_id: str,
    current_user=Depends(get_current_user),
    service: ResumeAnalysisService = Depends(
        get_resume_analysis_service
    ),
):
    analysis = await service.get_analysis(
        analysis_id=analysis_id,
        user_id=str(current_user.id),
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    return analysis


@router.delete(
    "/{analysis_id}",
    response_model=DeleteResumeAnalysisResponse,
)
async def delete_analysis(
    analysis_id: str,
    current_user=Depends(get_current_user),
    service: ResumeAnalysisService = Depends(
        get_resume_analysis_service
    ),
):
    deleted = await service.delete_analysis(
        analysis_id=analysis_id,
        user_id=str(current_user.id),
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    return {"message": "Analysis deleted successfully"}