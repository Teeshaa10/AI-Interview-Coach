from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InterviewQuestionRequest(BaseModel):
    """Validated input for resume-grounded interview question generation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    resume_id: str = Field(min_length=1, max_length=100)
    job_role: str = Field(min_length=2, max_length=120)
    experience_level: str = Field(min_length=2, max_length=80)
    number_of_questions: int = Field(default=10, ge=4, le=40)

    @field_validator("resume_id", "job_role", "experience_level")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value


class InterviewQuestionsResponse(BaseModel):
    """Structured question groups returned by Gemini and exposed by the API."""

    model_config = ConfigDict(extra="forbid")

    technical_questions: list[str]
    project_questions: list[str]
    hr_questions: list[str]
    coding_questions: list[str]

    @field_validator(
        "technical_questions",
        "project_questions",
        "hr_questions",
        "coding_questions",
    )
    @classmethod
    def clean_questions(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for value in values:
            question = value.strip()
            normalized = question.casefold()
            if question and normalized not in seen:
                cleaned.append(question)
                seen.add(normalized)
        return cleaned

    @model_validator(mode="after")
    def require_all_categories(self) -> "InterviewQuestionsResponse":
        categories = (
            self.technical_questions,
            self.project_questions,
            self.hr_questions,
            self.coding_questions,
        )
        if any(not category for category in categories):
            raise ValueError("Gemini must return at least one question in every category")
        return self

    @property
    def total_questions(self) -> int:
        return sum(
            len(category)
            for category in (
                self.technical_questions,
                self.project_questions,
                self.hr_questions,
                self.coding_questions,
            )
        )
