from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.dependencies import get_current_user
from app.models.user import UserInDB
from app.schemas.voice import (
    QuestionAudioRequest,
    TextToSpeechRequest,
    TextToSpeechResponse,
    VoiceInterviewAnswerResponse,
    VoiceTranscriptionResponse,
)
from app.services.voice_service import VoiceService
from app.voice_dependencies import get_voice_service


router = APIRouter(
    prefix="/voice",
    tags=["Voice Interview"],
)


@router.post(
    "/transcribe",
    response_model=VoiceTranscriptionResponse,
)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    result = await voice_service.transcribe_audio(
        audio_file
    )

    return VoiceTranscriptionResponse(
        transcription=result["transcription"],
        language=result.get("language"),
        duration_seconds=result.get(
            "duration_seconds"
        ),
        original_filename=result[
            "original_filename"
        ],
    )


@router.post(
    "/interview/{interview_id}/answer",
    response_model=VoiceInterviewAnswerResponse,
)
async def submit_voice_answer(
    interview_id: str,
    question_number: int = Form(..., ge=1),
    audio_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    result = await voice_service.submit_voice_answer(
        interview_id=interview_id,
        question_number=question_number,
        audio_file=audio_file,
        user_id=current_user.id,
    )

    return VoiceInterviewAnswerResponse(
        transcription=result["transcription"],
        language=result.get("language"),
        duration_seconds=result.get(
            "duration_seconds"
        ),
        question=result["question"],
    )


@router.post(
    "/text-to-speech",
    response_model=TextToSpeechResponse,
    status_code=status.HTTP_201_CREATED,
)
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    result = await voice_service.generate_text_audio(
        user_id=current_user.id,
        text=request.text,
        voice=request.voice,
    )

    return TextToSpeechResponse(
        audio_id=result["audio_id"],
        filename=result["filename"],
        content_type=result["content_type"],
        audio_url=result["audio_url"],
    )


@router.post(
    "/interview/{interview_id}/question-audio",
    response_model=TextToSpeechResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_question_audio(
    interview_id: str,
    request: QuestionAudioRequest,
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    result = await voice_service.generate_question_audio(
        interview_id=interview_id,
        question_number=request.question_number,
        user_id=current_user.id,
    )

    return TextToSpeechResponse(
        audio_id=result["audio_id"],
        filename=result["filename"],
        content_type=result["content_type"],
        audio_url=result["audio_url"],
    )


@router.get(
    "/audio/{audio_id}",
)
async def get_audio(
    audio_id: str,
    current_user: UserInDB = Depends(get_current_user),
    voice_service: VoiceService = Depends(get_voice_service),
):
    audio_record, audio_path = (
        await voice_service.get_audio_file(
            audio_id=audio_id,
            user_id=current_user.id,
        )
    )

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=audio_record["filename"],
    )