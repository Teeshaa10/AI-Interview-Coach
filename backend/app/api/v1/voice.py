from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse

from app.dependencies import get_current_user
from app.models.user import UserInDB
from app.schemas.voice import (
    TextToSpeechRequest,
    TextToSpeechResponse,
    TranscriptionResponse,
    VoiceAnswerResponse,
)
from app.services.voice_service import VoiceService
from app.voice_dependencies import get_voice_service

router = APIRouter(prefix="/voice", tags=["Voice Interview"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    del current_user
    try:
        transcription, language, duration = await voice_service.transcribe_upload(
            audio.file,
            audio.filename or "audio.webm",
        )
        return TranscriptionResponse(
            transcription=transcription,
            language=language,
            duration_seconds=duration,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await audio.close()


@router.post(
    "/interview/{interview_id}/answer",
    response_model=VoiceAnswerResponse,
)
async def submit_voice_answer(
    interview_id: str,
    question_number: int = Form(..., ge=1),
    audio: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    try:
        transcription, question = await voice_service.submit_voice_answer(
            user_id=current_user.id,
            interview_id=interview_id,
            question_number=question_number,
            file=audio.file,
            original_filename=audio.filename or "audio.webm",
        )
        return VoiceAnswerResponse(
            interview_id=interview_id,
            transcription=transcription,
            question=question,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await audio.close()


@router.post(
    "/text-to-speech",
    response_model=TextToSpeechResponse,
    status_code=status.HTTP_201_CREATED,
)
async def text_to_speech(
    payload: TextToSpeechRequest,
    request: Request,
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    try:
        record = await voice_service.synthesize_speech(
            user_id=current_user.id,
            text=payload.text,
            voice=payload.voice,
            rate=payload.rate,
            volume=payload.volume,
            pitch=payload.pitch,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TextToSpeechResponse(
        audio_id=record.id,
        audio_url=str(request.url_for("get_voice_audio", audio_id=record.id)),
        media_type=record.media_type,
        created_at=record.created_at,
    )


@router.get("/audio/{audio_id}", name="get_voice_audio")
async def get_voice_audio(
    audio_id: str,
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    try:
        path, record = await voice_service.get_owned_audio_path(
            user_id=current_user.id,
            audio_id=audio_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return FileResponse(
        path=path,
        media_type=record.media_type,
        filename=record.filename,
    )
