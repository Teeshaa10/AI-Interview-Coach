class InterviewError(Exception):
    """Base class for expected interview-question generation failures."""

    status_code = 500
    default_detail = "Interview questions could not be generated"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class EmptySemanticSearchResultsError(InterviewError):
    status_code = 422
    default_detail = "No resume content was available to generate interview questions"


class GeminiConfigurationError(InterviewError):
    status_code = 503
    default_detail = "Gemini is not configured on the server"


class GeminiAPIError(InterviewError):
    status_code = 502
    default_detail = "Gemini could not generate interview questions"


class GeminiTimeoutError(InterviewError):
    status_code = 504
    default_detail = "Gemini did not respond before the request timed out"


class InvalidGeminiResponseError(InterviewError):
    status_code = 502
    default_detail = "Gemini returned an invalid question response"
