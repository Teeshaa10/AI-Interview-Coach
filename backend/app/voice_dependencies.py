from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.interview_dependencies import get_evaluation_service, get_interview_repository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.voice_repository import VoiceRepository
from app.services.evaluation_service import EvaluationService
from app.services.voice_service import VoiceService


def get_voice_repository(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> VoiceRepository:
    return VoiceRepository(db)


def get_voice_service(
    interview_repository: InterviewRepository = Depends(get_interview_repository),
    voice_repository: VoiceRepository = Depends(get_voice_repository),
    evaluation_service: EvaluationService = Depends(get_evaluation_service),
    settings: Settings = Depends(get_settings),
) -> VoiceService:
    return VoiceService(
        interview_repository=interview_repository,
        voice_repository=voice_repository,
        evaluation_service=evaluation_service,
        audio_directory=settings.VOICE_AUDIO_DIR,
        whisper_model_name=settings.WHISPER_MODEL_NAME,
        whisper_device=settings.WHISPER_DEVICE,
        whisper_compute_type=settings.WHISPER_COMPUTE_TYPE,
        default_tts_voice=settings.TTS_DEFAULT_VOICE,
        max_audio_size_mb=settings.VOICE_MAX_AUDIO_SIZE_MB,
    )
