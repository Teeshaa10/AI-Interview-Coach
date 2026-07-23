from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.interview_session import InterviewQuestion


class TranscriptionResponse(BaseModel):
    transcription: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None


class VoiceAnswerResponse(BaseModel):
    interview_id: str
    transcription: str
    question: InterviewQuestion


class TextToSpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: Optional[str] = None
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"


class TextToSpeechResponse(BaseModel):
    audio_id: str
    audio_url: str
    media_type: str = "audio/mpeg"
    created_at: datetime


class VoiceAudioRecord(BaseModel):
    id: Optional[str] = None
    user_id: str
    filename: str
    media_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
