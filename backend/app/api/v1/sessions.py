from google import genai
from fastapi import APIRouter, Depends, Query, status

from app.core.config import Settings, get_settings
from app.dependencies import get_current_user
from app.models.user import UserInDB
from app.schemas.session_management import (
    AnalyticsInsightsResponse,
    UnifiedAnalyticsOverview,
    UnifiedHistoryResponse,
)
from app.services.session_management_service import SessionManagementService
from app.session_dependencies import get_gemini_client, get_session_management_service

router = APIRouter(prefix="/sessions", tags=["Unified Sessions"])


@router.get("/history", response_model=UnifiedHistoryResponse)
async def unified_history(
    type: str = Query("all", description="all | text | voice | coding"),
    status_filter: str = Query("all", alias="status", description="all | in_progress | completed"),
    search: str | None = Query(None, max_length=200),
    favorite_only: bool = Query(False),
    sort_by: str = Query("created_at", description="created_at | score | title"),
    sort_dir: str = Query("desc", description="asc | desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user),
    service: SessionManagementService = Depends(get_session_management_service),
):
    return await service.list_history(
        user_id=current_user.id,
        session_type=type,
        session_status=status_filter,
        search=search,
        favorite_only=favorite_only,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        limit=limit,
    )


@router.get("/analytics/overview", response_model=UnifiedAnalyticsOverview)
async def unified_analytics_overview(
    current_user: UserInDB = Depends(get_current_user),
    service: SessionManagementService = Depends(get_session_management_service),
):
    return await service.get_analytics_overview(current_user.id)


@router.get("/analytics/insights", response_model=AnalyticsInsightsResponse)
async def unified_analytics_insights(
    current_user: UserInDB = Depends(get_current_user),
    service: SessionManagementService = Depends(get_session_management_service),
    gemini_client: genai.Client | None = Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
):
    return await service.get_insights(
        current_user.id,
        gemini_client=gemini_client,
        model_name=settings.GEMINI_MODEL_NAME,
    )


@router.put("/{session_type}/{session_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def set_session_favorite(
    session_type: str,
    session_id: str,
    favorite: bool = Query(True),
    current_user: UserInDB = Depends(get_current_user),
    service: SessionManagementService = Depends(get_session_management_service),
):
    await service.toggle_favorite(current_user.id, session_type, session_id, favorite)


@router.delete("/{session_type}/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_type: str,
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    service: SessionManagementService = Depends(get_session_management_service),
):
    await service.delete_session(current_user.id, session_type, session_id)
