from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ResumeAnalysisRequest(BaseModel):
    resume_id: str = Field(min_length=1)
    target_role: str = Field(min_length=2, max_length=120)

    @field_validator("resume_id", "target_role")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ResumeAnalysisResult(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggested_skills: list[str] = Field(default_factory=list)
    suggested_projects: list[str] = Field(default_factory=list)
    improved_summary: str
    missing_keywords: list[str] = Field(default_factory=list)
    formatting_feedback: list[str] = Field(default_factory=list)
    actionable_recommendations: list[str] = Field(default_factory=list)


class ResumeAnalysisDocument(ResumeAnalysisResult):
    id: str
    user_id: str
    resume_id: str
    target_role: str
    created_at: datetime


class ResumeAnalysisHistoryResponse(BaseModel):
    analyses: list[ResumeAnalysisDocument]


class DeleteResumeAnalysisResponse(BaseModel):
    message: str