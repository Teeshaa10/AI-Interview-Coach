from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

# "text" and "voice" both live in the interview_sessions collection
# (InterviewSession.mode); "coding" lives in coding_interviews.
SessionType = Literal["text", "voice", "coding"]
SessionStatus = Literal["in_progress", "completed"]


class UnifiedSessionItem(BaseModel):
    """One row in the unified history list, regardless of which
    collection/module it actually came from."""

    session_id: str
    type: SessionType
    title: str
    subtitle: str = ""
    status: SessionStatus
    score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    resumable: bool
    resume_path: Optional[str] = None
    has_report: bool = False
    favorite: bool = False


class UnifiedHistoryResponse(BaseModel):
    sessions: list[UnifiedSessionItem]
    total: int
    page: int
    limit: int


class SessionTypeBreakdown(BaseModel):
    type: SessionType
    total: int
    completed: int
    in_progress: int
    average_score: float
    best_score: float


class AnalyticsTrendPoint(BaseModel):
    date: datetime
    type: SessionType
    score: float
    title: str


class UnifiedAnalyticsOverview(BaseModel):
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    average_score_overall: float
    best_score_overall: float
    lowest_score_overall: float
    # These two are only computed from text/voice interviews that have a
    # generated report (app.schemas.interview_report.InterviewReport already
    # tracks technical_score/communication_score per interview) - coding
    # sessions and un-reported interviews aren't part of this average.
    average_technical_score: float
    average_communication_score: float
    by_type: list[SessionTypeBreakdown]
    score_trend: list[AnalyticsTrendPoint]
    current_streak_days: int
    longest_streak_days: int
    strongest_topics: list[str] = []
    weakest_topics: list[str] = []


class AnalyticsInsightsResponse(BaseModel):
    insights: list[str]
    generated_by_ai: bool
