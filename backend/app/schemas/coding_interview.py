from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Difficulty = Literal["easy", "medium", "hard"]


class CodingExample(BaseModel):
    input: str
    output: str
    explanation: str = ""


class CodingTestCase(BaseModel):
    input: str
    expected_output: str


class ExpectedComplexity(BaseModel):
    time: str = ""
    space: str = ""


class CodingQuestion(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question_number: int
    title: str
    problem_statement: str
    difficulty: Difficulty = "medium"
    topics: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    examples: list[CodingExample] = Field(default_factory=list)
    function_signature: str = ""
    starter_code: dict[str, str] = Field(default_factory=dict)
    visible_test_cases: list[CodingTestCase] = Field(default_factory=list)
    hidden_test_cases: list[CodingTestCase] = Field(default_factory=list)
    expected_complexity: ExpectedComplexity = Field(default_factory=ExpectedComplexity)


class CodingQuestionPublic(CodingQuestion):
    hidden_test_cases: list[CodingTestCase] = Field(default_factory=list, exclude=True)


class CodingInterviewStartRequest(BaseModel):
    resume_id: str | None = None
    role: str = Field(min_length=2, max_length=120)
    experience_level: str = Field(default="Fresher", min_length=2, max_length=80)
    difficulty: Difficulty = "medium"
    topics: list[str] = Field(default_factory=list, max_length=10)
    language: str = "cpp"
    number_of_questions: int = Field(default=3, ge=1, le=5)


class CodingInterviewSession(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    user_id: str
    resume_id: str | None = None
    role: str
    experience_level: str
    difficulty: Difficulty
    language: str
    questions: list[CodingQuestion]
    completed: bool = False
    final_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class CodingInterviewResponse(BaseModel):
    session_id: str
    role: str
    difficulty: Difficulty
    language: str
    questions: list[CodingQuestionPublic]
    completed: bool
    final_score: float


class CodingSubmitRequest(BaseModel):
    question_number: int = Field(ge=1)
    language: str
    source_code: str = Field(min_length=1)
    explanation: str = ""


class TestExecutionResult(BaseModel):
    input: str
    expected_output: str
    actual_output: str = ""
    passed: bool
    stderr: str = ""
    execution_time: float | None = None


class CodingSubmission(BaseModel):
    id: str | None = None
    session_id: str
    user_id: str
    question_number: int
    language: str
    source_code: str
    explanation: str = ""
    test_results: list[TestExecutionResult] = Field(default_factory=list)
    tests_passed: int = 0
    tests_total: int = 0
    correctness_score: float = 0.0
    quality_score: float = 0.0
    complexity_score: float = 0.0
    explanation_score: float = 0.0
    overall_score: float = 0.0
    feedback: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CodingSubmitResponse(BaseModel):
    submission: CodingSubmission
    next_question: CodingQuestionPublic | None = None


class CodingHistoryResponse(BaseModel):
    sessions: list[CodingInterviewResponse]
    page: int
    limit: int
    total: int


class SupportedLanguagesResponse(BaseModel):
    provider: str
    languages: list[str]
