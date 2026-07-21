from pathlib import Path
from uuid import uuid4

import edge_tts

from app.core.config import Settings
from app.exceptions.voice import TextToSpeechError
from app.repositories.voice_repository import VoiceRepository


class TextToSpeechService:
    def __init__(
        self,
        settings: Settings,
        voice_repository: VoiceRepository,
    ):
        self.settings = settings
        self.voice_repository = voice_repository

    def _get_audio_directory(self) -> Path:
        audio_directory = Path(
            self.settings.VOICE_AUDIO_DIR
        ).resolve()

        audio_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return audio_directory

    async def generate_audio(
        self,
        user_id: str,
        text: str,
        voice: str | None = None,
    ) -> dict:
        clean_text = text.strip()

        if not clean_text:
            raise TextToSpeechError(
                "Text must not be empty"
            )

        if len(clean_text) > self.settings.TTS_MAX_TEXT_LENGTH:
            raise TextToSpeechError(
                "Text exceeds the maximum allowed length"
            )

        selected_voice = (
            voice.strip()
            if voice and voice.strip()
            else self.settings.TTS_DEFAULT_VOICE
        )

        audio_directory = self._get_audio_directory()

        stored_filename = f"{uuid4().hex}.mp3"
        output_path = (
            audio_directory / stored_filename
        ).resolve()

        if audio_directory not in output_path.parents:
            raise TextToSpeechError(
                "Invalid audio output path"
            )

        try:
            communicator = edge_tts.Communicate(
                clean_text,
                selected_voice,
            )

            await communicator.save(
                str(output_path)
            )

            if (
                not output_path.exists()
                or output_path.stat().st_size == 0
            ):
                raise TextToSpeechError(
                    "Generated audio file is empty"
                )

            audio_record = (
                await self.voice_repository.create_audio_record(
                    user_id=user_id,
                    filename=stored_filename,
                    stored_filename=stored_filename,
                    content_type="audio/mpeg",
                    file_path=str(output_path),
                    voice=selected_voice,
                    text_length=len(clean_text),
                )
            )

            audio_id = audio_record["id"]

            return {
                "audio_id": audio_id,
                "filename": stored_filename,
                "content_type": "audio/mpeg",
                "audio_url": f"/voice/audio/{audio_id}",
            }

        except TextToSpeechError:
            if output_path.exists():
                output_path.unlink(missing_ok=True)

            raise

        except Exception as exc:
            if output_path.exists():
                output_path.unlink(missing_ok=True)

            raise TextToSpeechError(
                "Text-to-speech generation failed"
            ) from exc

    async def get_user_audio(
        self,
        audio_id: str,
        user_id: str,
    ) -> tuple[dict, Path]:
        audio_record = (
            await self.voice_repository.get_user_audio(
                audio_id=audio_id,
                user_id=user_id,
            )
        )

        if not audio_record:
            return {}, Path()

        audio_directory = self._get_audio_directory()

        audio_path = Path(
            audio_record["file_path"]
        ).resolve()

        if audio_directory not in audio_path.parents:
            raise TextToSpeechError(
                "Invalid stored audio path"
            )

        return audio_record, audio_path