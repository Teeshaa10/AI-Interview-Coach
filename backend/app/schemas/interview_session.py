from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    question_number: int
    question: str
    category: str

    answer: Optional[str] = None

    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    completeness_score: Optional[float] = None
    overall_score: Optional[float] = None

    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

    better_answer: Optional[str] = None
    feedback: Optional[str] = None


class InterviewSessionCreate(BaseModel):
    resume_id: str
    job_role: str
    experience_level: str
    number_of_questions: int = Field(
        default=10,
        ge=4,
        le=40,
    )
    # Module 6/7: distinguishes a text-answered session from a voice-answered
    # one. Both flows create their session via the same POST /interview/start
    # endpoint, so this is optional and defaults to "text" to stay backward
    # compatible with any existing caller that doesn't send it.
    mode: str = "text"


class InterviewSession(BaseModel):
    id: Optional[str] = None

    user_id: str
    resume_id: str

    job_role: str
    experience_level: str

    questions: List[InterviewQuestion]

    average_score: float = 0.0

    completed: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)

    completed_at: Optional[datetime] = None

    # Defaults to "text" so documents created before Module 6/7 (which have
    # no "mode" field stored) still validate correctly.
    mode: str = "text"

    favorite: bool = False


class InterviewSessionResponse(BaseModel):
    interview_id: str
    questions: List[InterviewQuestion]


class SubmitAnswerRequest(BaseModel):
    question_number: int
    answer: str = Field(min_length=1)


class SubmitAnswerResponse(BaseModel):
    question: InterviewQuestion


class FinishInterviewResponse(BaseModel):
    interview_id: str
    average_score: float
    completed: bool


class InterviewHistoryItem(BaseModel):
    interview_id: str
    job_role: str
    experience_level: str
    average_score: float
    completed: bool
    created_at: datetime
    mode: str = "text"


class InterviewHistoryResponse(BaseModel):
    interviews: List[InterviewHistoryItem]