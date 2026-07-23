import asyncio
import re
import threading
import uuid
from pathlib import Path
from typing import BinaryIO, Optional

import edge_tts
from faster_whisper import WhisperModel

from app.repositories.interview_repository import InterviewRepository
from app.repositories.voice_repository import VoiceRepository
from app.schemas.interview_evaluation import InterviewEvaluationResponse
from app.schemas.voice import VoiceAudioRecord
from app.services.evaluation_service import EvaluationService


class VoiceService:
    _whisper_models: dict[tuple[str, str, str], WhisperModel] = {}
    _whisper_model_lock = threading.Lock()

    ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".aac"}

    def __init__(
        self,
        interview_repository: InterviewRepository,
        voice_repository: VoiceRepository,
        evaluation_service: EvaluationService,
        audio_directory: str,
        whisper_model_name: str,
        whisper_device: str,
        whisper_compute_type: str,
        default_tts_voice: str,
        max_audio_size_mb: int,
    ):
        self.interview_repository = interview_repository
        self.voice_repository = voice_repository
        self.evaluation_service = evaluation_service
        self.audio_directory = Path(audio_directory).resolve()
        self.audio_directory.mkdir(parents=True, exist_ok=True)
        self.whisper_model_name = whisper_model_name
        self.whisper_device = whisper_device
        self.whisper_compute_type = whisper_compute_type
        self.default_tts_voice = default_tts_voice
        self.max_audio_size_bytes = max_audio_size_mb * 1024 * 1024

    async def _get_whisper_model(self) -> WhisperModel:
        key = (
            self.whisper_model_name,
            self.whisper_device,
            self.whisper_compute_type,
        )

        def load_model() -> WhisperModel:
            with self._whisper_model_lock:
                model = self._whisper_models.get(key)
                if model is None:
                    model = WhisperModel(
                        self.whisper_model_name,
                        device=self.whisper_device,
                        compute_type=self.whisper_compute_type,
                    )
                    self._whisper_models[key] = model
                return model

        return await asyncio.to_thread(load_model)

    async def save_uploaded_audio(self, file: BinaryIO, original_filename: str) -> Path:
        extension = Path(original_filename or "audio.webm").suffix.lower()
        if extension not in self.ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError("Unsupported audio format")

        destination = self.audio_directory / f"upload_{uuid.uuid4().hex}{extension}"
        size = 0

        try:
            with destination.open("wb") as output:
                while chunk := file.read(1024 * 1024):
                    size += len(chunk)
                    if size > self.max_audio_size_bytes:
                        raise ValueError("Audio file is too large")
                    output.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        if size == 0:
            destination.unlink(missing_ok=True)
            raise ValueError("Audio file is empty")

        return destination

    async def transcribe_file(self, audio_path: Path) -> tuple[str, Optional[str], Optional[float]]:
        model = await self._get_whisper_model()

        def transcribe() -> tuple[str, Optional[str], Optional[float]]:
            segments, info = model.transcribe(
                str(audio_path),
                beam_size=5,
                vad_filter=True,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            language = getattr(info, "language", None)
            duration = getattr(info, "duration", None)
            return text, language, duration

        text, language, duration = await asyncio.to_thread(transcribe)
        if not text:
            raise ValueError("No speech could be detected in the audio")

        return text, language, duration

    async def transcribe_upload(
        self,
        file: BinaryIO,
        original_filename: str,
    ) -> tuple[str, Optional[str], Optional[float]]:
        audio_path = await self.save_uploaded_audio(file, original_filename)
        try:
            return await self.transcribe_file(audio_path)
        finally:
            audio_path.unlink(missing_ok=True)

    async def submit_voice_answer(
        self,
        user_id: str,
        interview_id: str,
        question_number: int,
        file: BinaryIO,
        original_filename: str,
    ):
        interview = await self.interview_repository.get_interview_by_id(interview_id)
        if interview is None:
            raise LookupError("Interview not found")
        if interview.user_id != user_id:
            raise PermissionError("Access denied")
        if question_number < 1 or question_number > len(interview.questions):
            raise ValueError("Invalid question number")

        transcription, _, _ = await self.transcribe_upload(file, original_filename)
        question = interview.questions[question_number - 1]

        evaluation: InterviewEvaluationResponse = await self.evaluation_service.evaluate_answer(
            question=question.question,
            answer=transcription,
            resume_context="",
            job_role=interview.job_role,
            experience_level=interview.experience_level,
        )

        question.answer = transcription
        question.technical_score = evaluation.technical_score
        question.communication_score = evaluation.communication_score
        question.completeness_score = evaluation.completeness_score
        question.overall_score = evaluation.overall_score
        question.strengths = evaluation.strengths
        question.weaknesses = evaluation.weaknesses
        question.better_answer = evaluation.better_answer
        question.feedback = evaluation.feedback

        await self.interview_repository.update_question(
            interview_id,
            question_number,
            question.model_dump(),
        )

        return transcription, question

    async def synthesize_speech(
        self,
        user_id: str,
        text: str,
        voice: Optional[str],
        rate: str,
        volume: str,
        pitch: str,
    ) -> VoiceAudioRecord:
        selected_voice = voice or self.default_tts_voice
        self._validate_tts_adjustment(rate, r"^[+-]\d+%$", "rate")
        self._validate_tts_adjustment(volume, r"^[+-]\d+%$", "volume")
        self._validate_tts_adjustment(pitch, r"^[+-]\d+Hz$", "pitch")

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        output_path = self.audio_directory / filename

        communicator = edge_tts.Communicate(
            text=text,
            voice=selected_voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )

        try:
            await communicator.save(str(output_path))
        except Exception:
            output_path.unlink(missing_ok=True)
            raise

        record = VoiceAudioRecord(
            user_id=user_id,
            filename=filename,
            media_type="audio/mpeg",
        )
        record.id = await self.voice_repository.create_audio_record(record)
        return record

    async def get_owned_audio_path(
        self,
        user_id: str,
        audio_id: str,
    ) -> tuple[Path, VoiceAudioRecord]:
        record = await self.voice_repository.get_audio_record(audio_id)
        if record is None:
            raise LookupError("Audio not found")
        if record.user_id != user_id:
            raise PermissionError("Access denied")

        path = (self.audio_directory / record.filename).resolve()
        if self.audio_directory not in path.parents or not path.is_file():
            raise LookupError("Audio file not found")

        return path, record

    @staticmethod
    def _validate_tts_adjustment(value: str, pattern: str, field_name: str) -> None:
        if not re.fullmatch(pattern, value):
            raise ValueError(f"Invalid text-to-speech {field_name}")
