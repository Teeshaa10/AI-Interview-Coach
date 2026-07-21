from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.interview_session import InterviewQuestion


class VoiceTranscriptionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcription: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    original_filename: str


class VoiceInterviewAnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transcription: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    question: InterviewQuestion


class TextToSpeechRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    text: str = Field(min_length=1, max_length=3000)
    voice: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Text must not be blank")

        return value

    @field_validator("voice")
    @classmethod
    def validate_voice(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value


class QuestionAudioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_number: int = Field(ge=1)


class TextToSpeechResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audio_id: str
    filename: str
    content_type: str = "audio/mpeg"
    audio_url: str