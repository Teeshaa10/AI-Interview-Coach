import asyncio
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import Settings
from app.exceptions.voice import (
    AudioTranscriptionError,
    EmptyTranscriptionError,
)


class SpeechToTextService:
    _model: Any = None
    _model_lock = Lock()

    def __init__(self, settings: Settings):
        self.settings = settings

    def _get_model(self) -> Any:
        if self.__class__._model is not None:
            return self.__class__._model

        with self.__class__._model_lock:
            if self.__class__._model is not None:
                return self.__class__._model

            try:
                from faster_whisper import WhisperModel

                self.__class__._model = WhisperModel(
                    self.settings.WHISPER_MODEL_NAME,
                    device=self.settings.WHISPER_DEVICE,
                    compute_type=self.settings.WHISPER_COMPUTE_TYPE,
                )
            except Exception as exc:
                raise AudioTranscriptionError(
                    "Whisper model could not be loaded"
                ) from exc

        return self.__class__._model

    def _transcribe_sync(self, file_path: Path) -> dict:
        try:
            model = self._get_model()

            segments, info = model.transcribe(
                str(file_path),
                beam_size=5,
                vad_filter=True,
            )

            transcription_parts: list[str] = []

            for segment in segments:
                text = str(segment.text).strip()

                if text:
                    transcription_parts.append(text)

            transcription = " ".join(transcription_parts).strip()

            if not transcription:
                raise EmptyTranscriptionError()

            language = getattr(info, "language", None)
            duration = getattr(info, "duration", None)

            return {
                "transcription": transcription,
                "language": language,
                "duration_seconds": (
                    float(duration)
                    if duration is not None
                    else None
                ),
            }

        except EmptyTranscriptionError:
            raise
        except AudioTranscriptionError:
            raise
        except Exception as exc:
            raise AudioTranscriptionError(
                "The uploaded audio could not be processed"
            ) from exc

    async def transcribe(self, file_path: Path) -> dict:
        return await asyncio.to_thread(
            self._transcribe_sync,
            file_path,
        )