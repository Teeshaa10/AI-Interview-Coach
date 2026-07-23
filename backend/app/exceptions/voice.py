class VoiceError(Exception):
    """Base exception for expected voice-module failures."""

    status_code = 500
    default_detail = "Voice operation failed"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class UnsupportedAudioFormatError(VoiceError):
    status_code = 415
    default_detail = "Unsupported audio format"


class EmptyAudioFileError(VoiceError):
    status_code = 422
    default_detail = "The uploaded audio file is empty"


class AudioFileTooLargeError(VoiceError):
    status_code = 413
    default_detail = "The uploaded audio file exceeds the allowed size"


class AudioTranscriptionError(VoiceError):
    status_code = 422
    default_detail = "The audio file could not be transcribed"


class EmptyTranscriptionError(VoiceError):
    status_code = 422
    default_detail = "No speech could be detected in the uploaded audio"


class TextToSpeechError(VoiceError):
    status_code = 502
    default_detail = "The text-to-speech audio could not be generated"


class AudioNotFoundError(VoiceError):
    status_code = 404
    default_detail = "Audio file not found"


class ForbiddenAudioAccessError(VoiceError):
    status_code = 403
    default_detail = "You do not have permission to access this audio file"


class UnsafeAudioPathError(VoiceError):
    status_code = 400
    default_detail = "Invalid audio file path"


class InterviewNotFoundForVoiceError(VoiceError):
    status_code = 404
    default_detail = "Interview session not found"


class ForbiddenVoiceInterviewError(VoiceError):
    status_code = 403
    default_detail = "You do not have permission to access this interview"


class VoiceInterviewCompletedError(VoiceError):
    status_code = 409
    default_detail = "This interview has already been completed"


class VoiceQuestionNotFoundError(VoiceError):
    status_code = 404
    default_detail = "Interview question not found"