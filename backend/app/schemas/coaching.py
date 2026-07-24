from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.session_management import SessionTypeBreakdown

ReadinessLevel = Literal["getting_started", "building_confidence", "interview_ready", "highly_prepared"]
InterviewType = Literal["text", "voice", "coding"]
PlanDuration = Literal[7, 14, 30]


class CoachingProfile(BaseModel):
    """Snapshot of a user's practice history, built entirely from data the
    project already has (unified analytics + resume + interview history) -
    no duplicate score/streak computation, per the Module 9 requirements."""

    is_new_user: bool
    has_resume: bool
    target_role: str | None = None
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    average_score_overall: float
    average_technical_score: float
    average_communication_score: float
    current_streak_days: int
    longest_streak_days: int
    strongest_topics: list[str] = Field(default_factory=list)
    weakest_topics: list[str] = Field(default_factory=list)
    by_type: list[SessionTypeBreakdown] = Field(default_factory=list)


class CoachingInsights(BaseModel):
    readiness_level: ReadinessLevel
    readiness_score: float = Field(ge=0, le=100)
    top_strengths: list[str] = Field(default_factory=list)
    priority_weaknesses: list[str] = Field(default_factory=list)
    recommended_topics: list[str] = Field(default_factory=list)
    consistency_insight: str
    next_milestone: str
    ai_summary: str | None = None
    generated_by_ai: bool = False


class NextInterviewRecommendation(BaseModel):
    interview_type: InterviewType
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    target_skill: str
    reason: str
    suggested_duration_minutes: int
    suggested_number_of_questions: int
    setup_path: str


class PracticePlanItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    item_id: str
    day_number: int
    focus_area: str
    interview_type: InterviewType
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    estimated_minutes: int
    objective: str
    recommended_activity: str
    reason: str | None = None
    completed: bool = False


class PracticePlan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    user_id: str
    duration_days: PlanDuration
    items: list[PracticePlanItem]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def completion_percentage(self) -> float:
        if not self.items:
            return 0.0
        done = sum(1 for item in self.items if item.completed)
        return round((done / len(self.items)) * 100, 1)


class PracticePlanResponse(BaseModel):
    id: str
    duration_days: PlanDuration
    items: list[PracticePlanItem]
    completed_items: int
    total_items: int
    completion_percentage: float
    created_at: datetime


class CreatePlanRequest(BaseModel):
    duration_days: PlanDuration = 7


class PlanItemUpdateRequest(BaseModel):
    completed: bool
