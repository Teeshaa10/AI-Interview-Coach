from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.interview_dependencies import (
    get_evaluation_service,
    get_interview_repository,
)
from app.repositories.interview_repository import InterviewRepository
from app.repositories.voice_repository import VoiceRepository
from app.services.evaluation_service import EvaluationService
from app.services.speech_to_text_service import SpeechToTextService
from app.services.text_to_speech_service import TextToSpeechService
from app.services.voice_service import VoiceService


def get_voice_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> VoiceRepository:
    return VoiceRepository(db)


def get_speech_to_text_service(
    settings: Settings = Depends(get_settings),
) -> SpeechToTextService:
    return SpeechToTextService(settings)


def get_text_to_speech_service(
    settings: Settings = Depends(get_settings),
    voice_repository: VoiceRepository = Depends(
        get_voice_repository
    ),
) -> TextToSpeechService:
    return TextToSpeechService(
        settings=settings,
        voice_repository=voice_repository,
    )


def get_voice_service(
    settings: Settings = Depends(get_settings),
    speech_to_text_service: SpeechToTextService = Depends(
        get_speech_to_text_service
    ),
    text_to_speech_service: TextToSpeechService = Depends(
        get_text_to_speech_service
    ),
    interview_repository: InterviewRepository = Depends(
        get_interview_repository
    ),
    evaluation_service: EvaluationService = Depends(
        get_evaluation_service
    ),
) -> VoiceService:
    return VoiceService(
        settings=settings,
        speech_to_text_service=speech_to_text_service,
        text_to_speech_service=text_to_speech_service,
        interview_repository=interview_repository,
        evaluation_service=evaluation_service,
    )