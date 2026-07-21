from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import UploadFile

from app.core.config import Settings
from app.exceptions.voice import (
    AudioFileTooLargeError,
    AudioNotFoundError,
    EmptyAudioFileError,
    ForbiddenAudioAccessError,
    ForbiddenVoiceInterviewError,
    InterviewNotFoundForVoiceError,
    UnsupportedAudioFormatError,
    UnsafeAudioPathError,
    VoiceInterviewCompletedError,
    VoiceQuestionNotFoundError,
)
from app.repositories.interview_repository import InterviewRepository
from app.schemas.interview_evaluation import InterviewEvaluationResponse
from app.schemas.interview_session import InterviewQuestion
from app.services.evaluation_service import EvaluationService
from app.services.speech_to_text_service import SpeechToTextService
from app.services.text_to_speech_service import TextToSpeechService


class VoiceService:
    ALLOWED_EXTENSIONS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".webm",
        ".ogg",
        ".flac",
        ".mp4",
    }

    ALLOWED_CONTENT_TYPES = {
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/x-m4a",
        "audio/m4a",
        "audio/webm",
        "video/webm",
        "audio/ogg",
        "application/ogg",
        "audio/flac",
        "audio/x-flac",
        "video/mp4",
    }

    READ_CHUNK_SIZE = 1024 * 1024

    def __init__(
        self,
        *,
        settings: Settings,
        speech_to_text_service: SpeechToTextService,
        text_to_speech_service: TextToSpeechService,
        interview_repository: InterviewRepository,
        evaluation_service: EvaluationService,
    ) -> None:
        self.settings = settings
        self.speech_to_text_service = speech_to_text_service
        self.text_to_speech_service = text_to_speech_service
        self.interview_repository = interview_repository
        self.evaluation_service = evaluation_service

    def _validate_audio_metadata(
        self,
        audio_file: UploadFile,
    ) -> str:
        original_filename = (
            audio_file.filename or "audio"
        ).strip()

        extension = Path(
            original_filename
        ).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise UnsupportedAudioFormatError(
                "Supported formats are WAV, MP3, M4A, WEBM, OGG, FLAC and MP4"
            )

        content_type = (
            audio_file.content_type or ""
        ).lower()

        if (
            content_type
            and content_type
            not in self.ALLOWED_CONTENT_TYPES
        ):
            raise UnsupportedAudioFormatError(
                f"Unsupported audio content type: {content_type}"
            )

        return extension

    async def _save_temporary_audio(
        self,
        audio_file: UploadFile,
    ) -> tuple[Path, str]:
        extension = self._validate_audio_metadata(
            audio_file
        )

        original_filename = (
            audio_file.filename or f"audio{extension}"
        )

        maximum_size = (
            self.settings.VOICE_MAX_AUDIO_SIZE_MB
            * 1024
            * 1024
        )

        total_size = 0
        temporary_path: Path | None = None

        try:
            with NamedTemporaryFile(
                mode="wb",
                suffix=extension,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(
                    temporary_file.name
                )

                while True:
                    chunk = await audio_file.read(
                        self.READ_CHUNK_SIZE
                    )

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > maximum_size:
                        raise AudioFileTooLargeError(
                            (
                                "Audio file exceeds the "
                                f"{self.settings.VOICE_MAX_AUDIO_SIZE_MB} MB limit"
                            )
                        )

                    temporary_file.write(chunk)

            if total_size == 0:
                raise EmptyAudioFileError()

            return temporary_path, original_filename

        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(
                    missing_ok=True
                )

            raise

        finally:
            await audio_file.close()

    async def transcribe_audio(
        self,
        audio_file: UploadFile,
    ) -> dict:
        temporary_path: Path | None = None

        try:
            (
                temporary_path,
                original_filename,
            ) = await self._save_temporary_audio(
                audio_file
            )

            transcription_result = (
                await self.speech_to_text_service.transcribe(
                    temporary_path
                )
            )

            return {
                **transcription_result,
                "original_filename": original_filename,
            }

        finally:
            if temporary_path is not None:
                temporary_path.unlink(
                    missing_ok=True
                )

    async def submit_voice_answer(
        self,
        *,
        interview_id: str,
        question_number: int,
        audio_file: UploadFile,
        user_id: str,
    ) -> dict:
        interview = (
            await self.interview_repository.get_interview_by_id(
                interview_id
            )
        )

        if interview is None:
            raise InterviewNotFoundForVoiceError()

        if interview.user_id != user_id:
            raise ForbiddenVoiceInterviewError()

        if interview.completed:
            raise VoiceInterviewCompletedError()

        if (
            question_number < 1
            or question_number
            > len(interview.questions)
        ):
            raise VoiceQuestionNotFoundError(
                "Invalid interview question number"
            )

        transcription_result = (
            await self.transcribe_audio(
                audio_file
            )
        )

        transcription = transcription_result[
            "transcription"
        ]

        question = interview.questions[
            question_number - 1
        ]

        evaluation: InterviewEvaluationResponse = (
            await self.evaluation_service.evaluate_answer(
                question=question.question,
                answer=transcription,
                resume_context="",
                job_role=interview.job_role,
                experience_level=(
                    interview.experience_level
                ),
            )
        )

        updated_question = InterviewQuestion(
            question_number=question.question_number,
            question=question.question,
            category=question.category,
            answer=transcription,
            technical_score=evaluation.technical_score,
            communication_score=(
                evaluation.communication_score
            ),
            completeness_score=(
                evaluation.completeness_score
            ),
            overall_score=evaluation.overall_score,
            strengths=evaluation.strengths,
            weaknesses=evaluation.weaknesses,
            better_answer=evaluation.better_answer,
            feedback=evaluation.feedback,
        )

        await self.interview_repository.update_question(
            interview_id,
            question_number,
            updated_question.model_dump(),
        )

        return {
            "transcription": transcription,
            "language": transcription_result.get(
                "language"
            ),
            "duration_seconds": (
                transcription_result.get(
                    "duration_seconds"
                )
            ),
            "question": updated_question,
        }

    async def generate_text_audio(
        self,
        *,
        user_id: str,
        text: str,
        voice: str | None,
    ) -> dict:
        return (
            await self.text_to_speech_service.generate_audio(
                user_id=user_id,
                text=text,
                voice=voice,
            )
        )

    async def generate_question_audio(
        self,
        *,
        interview_id: str,
        question_number: int,
        user_id: str,
        voice: str | None = None,
    ) -> dict:
        interview = (
            await self.interview_repository.get_interview_by_id(
                interview_id
            )
        )

        if interview is None:
            raise InterviewNotFoundForVoiceError()

        if interview.user_id != user_id:
            raise ForbiddenVoiceInterviewError()

        if (
            question_number < 1
            or question_number
            > len(interview.questions)
        ):
            raise VoiceQuestionNotFoundError(
                "Invalid interview question number"
            )

        question = interview.questions[
            question_number - 1
        ]

        return (
            await self.text_to_speech_service.generate_audio(
                user_id=user_id,
                text=question.question,
                voice=voice,
            )
        )

    async def get_audio_file(
        self,
        *,
        audio_id: str,
        user_id: str,
    ) -> tuple[dict, Path]:
        audio_record, audio_path = (
            await self.text_to_speech_service.get_user_audio(
                audio_id=audio_id,
                user_id=user_id,
            )
        )

        if not audio_record:
            existing_record = (
                await self.text_to_speech_service
                .voice_repository
                .get_audio_by_id(audio_id)
            )

            if existing_record:
                raise ForbiddenAudioAccessError()

            raise AudioNotFoundError()

        if not audio_path:
            raise AudioNotFoundError()

        audio_directory = Path(
            self.settings.VOICE_AUDIO_DIR
        ).resolve()

        resolved_audio_path = audio_path.resolve()

        if (
            audio_directory
            not in resolved_audio_path.parents
        ):
            raise UnsafeAudioPathError()

        if (
            not resolved_audio_path.exists()
            or not resolved_audio_path.is_file()
        ):
            raise AudioNotFoundError(
                "Audio metadata exists, but the generated file is missing"
            )

        return audio_record, resolved_audio_path