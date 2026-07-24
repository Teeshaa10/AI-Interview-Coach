from fastapi import APIRouter, Depends, status

from app.coaching_dependencies import get_coaching_service
from app.dependencies import get_current_user
from app.exceptions.coaching import PracticePlanNotFoundError
from app.models.user import UserInDB
from app.schemas.coaching import (
    CoachingInsights,
    CoachingProfile,
    CreatePlanRequest,
    NextInterviewRecommendation,
    PlanItemUpdateRequest,
    PracticePlanResponse,
)
from app.services.coaching_service import CoachingService

router = APIRouter(prefix="/coaching", tags=["AI Coaching"])


@router.get("/profile", response_model=CoachingProfile)
async def get_coaching_profile(
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.build_profile(current_user.id)


@router.get("/insights", response_model=CoachingInsights)
async def get_coaching_insights(
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.get_insights(current_user.id)


@router.get("/recommendation", response_model=NextInterviewRecommendation)
async def get_recommendation(
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.get_recommendation(current_user.id)


@router.get("/plans/active", response_model=PracticePlanResponse | None)
async def get_active_plan(
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.get_active_plan(current_user.id)


@router.post("/plans", response_model=PracticePlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    request: CreatePlanRequest,
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.create_plan(current_user.id, request.duration_days)


@router.post("/plans/{plan_id}/regenerate", response_model=PracticePlanResponse)
async def regenerate_plan(
    plan_id: str,
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.regenerate_plan(current_user.id, plan_id)


@router.patch("/plans/{plan_id}/items/{item_id}", response_model=PracticePlanResponse)
async def update_plan_item(
    plan_id: str,
    item_id: str,
    request: PlanItemUpdateRequest,
    current_user: UserInDB = Depends(get_current_user),
    service: CoachingService = Depends(get_coaching_service),
):
    return await service.set_item_completion(current_user.id, plan_id, item_id, request.completed)
