from fastapi import status


class CodingError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class CodingSessionNotFoundError(CodingError):
    def __init__(self):
        super().__init__("Coding interview session not found", status.HTTP_404_NOT_FOUND)


class CodingSessionCompletedError(CodingError):
    def __init__(self):
        super().__init__("Coding interview session is already completed", status.HTTP_409_CONFLICT)


class CodingQuestionNotFoundError(CodingError):
    def __init__(self):
        super().__init__("Coding question not found", status.HTTP_404_NOT_FOUND)


class UnsupportedLanguageError(CodingError):
    def __init__(self, language: str):
        super().__init__(f"Unsupported language: {language}", status.HTTP_400_BAD_REQUEST)


class SourceCodeTooLargeError(CodingError):
    def __init__(self):
        super().__init__("Source code exceeds the configured size limit", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class ExecutionProviderUnavailableError(CodingError):
    def __init__(self):
        super().__init__("Code execution provider is not configured or unavailable", status.HTTP_503_SERVICE_UNAVAILABLE)


class ExecutionFailureError(CodingError):
    def __init__(self, detail: str = "Code execution failed"):
        super().__init__(detail, status.HTTP_502_BAD_GATEWAY)


class MalformedCodingQuestionError(CodingError):
    def __init__(self):
        super().__init__("Gemini returned malformed coding questions", status.HTTP_502_BAD_GATEWAY)


class ForbiddenCodingAccessError(CodingError):
    def __init__(self):
        super().__init__("Access denied", status.HTTP_403_FORBIDDEN)
