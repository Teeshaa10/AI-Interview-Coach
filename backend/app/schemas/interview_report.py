from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuestionReportItem(BaseModel):
    question_number: int
    question: str
    category: str
    answer: str | None = None
    technical_score: float | None = None
    communication_score: float | None = None
    completeness_score: float | None = None
    overall_score: float | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    feedback: str | None = None
    improved_answer: str | None = None


class InterviewReport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    user_id: str
    interview_id: str
    job_role: str
    experience_level: str
    total_questions: int
    answered_questions: int
    completion_percentage: float
    overall_score: float
    technical_score: float
    communication_score: float
    completeness_score: float
    category_scores: dict[str, float] = Field(default_factory=dict)
    question_breakdown: list[QuestionReportItem] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    improvement_plan: list[str] = Field(default_factory=list)
    recommended_next_difficulty: str
    summary: str
    interview_completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GenerateReportRequest(BaseModel):
    regenerate: bool = False


class ReportHistoryResponse(BaseModel):
    reports: list[InterviewReport]
    page: int
    limit: int
    total: int


class ScoreTrendPoint(BaseModel):
    date: datetime
    overall_score: float
    technical_score: float
    communication_score: float


class ReportAnalyticsSummary(BaseModel):
    interviews_completed: int
    average_overall_score: float
    best_score: float
    latest_score: float
    technical_average: float
    communication_average: float
    completeness_average: float
    strongest_topics: list[str]
    weakest_topics: list[str]
    recent_improvement_percentage: float | None
    score_trend: list[ScoreTrendPoint]


class ReportTrendsResponse(BaseModel):
    grouping: Literal["weekly", "monthly"]
    points: list[dict]
