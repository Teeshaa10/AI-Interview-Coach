from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InterviewQuestionRequest(BaseModel):
    """
    Request schema for generating AI interview questions.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    resume_id: str = Field(min_length=1, max_length=100)
    job_role: str = Field(min_length=2, max_length=120)
    experience_level: str = Field(min_length=2, max_length=80)
    number_of_questions: int = Field(
        default=10,
        ge=4,
        le=40,
    )

    @field_validator(
        "resume_id",
        "job_role",
        "experience_level",
    )
    @classmethod
    def validate_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value


class InterviewQuestionsResponse(BaseModel):
    """
    Structured questions returned by Gemini.
    """

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
    def remove_duplicates(cls, questions: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for question in questions:
            question = question.strip()

            if not question:
                continue

            key = question.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(question)

        return cleaned

    @model_validator(mode="after")
    def validate_categories(self):
        if not self.technical_questions:
            raise ValueError("technical_questions cannot be empty")

        if not self.project_questions:
            raise ValueError("project_questions cannot be empty")

        if not self.hr_questions:
            raise ValueError("hr_questions cannot be empty")

        if not self.coding_questions:
            raise ValueError("coding_questions cannot be empty")

        return self

    @property
    def total_questions(self) -> int:
        return (
            len(self.technical_questions)
            + len(self.project_questions)
            + len(self.hr_questions)
            + len(self.coding_questions)
        )