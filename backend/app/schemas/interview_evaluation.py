from typing import List

from pydantic import BaseModel, Field


class InterviewEvaluationResponse(BaseModel):
    technical_score: float = Field(..., ge=0, le=10)
    communication_score: float = Field(..., ge=0, le=10)
    completeness_score: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)

    strengths: List[str]
    weaknesses: List[str]

    better_answer: str
    feedback: str