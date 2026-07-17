class ResumeError(Exception):
    """
    Base exception for expected resume-module failures.

    Services raise domain exceptions instead of FastAPI HTTPException objects.
    The API layer maps these errors to HTTP responses.
    """

    status_code = 500
    default_detail = "A resume processing error occurred"

    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.detail = detail or self.default_detail
        self.headers = headers
        super().__init__(self.detail)


class InvalidResumeFileError(ResumeError):
    """Raised when the uploaded file type or contents are invalid."""

    status_code = 415
    default_detail = "Only valid PDF and DOCX files are supported"


class ResumeFileTooLargeError(ResumeError):
    """Raised when the uploaded resume exceeds the configured size limit."""

    status_code = 413
    default_detail = "The uploaded resume exceeds the maximum allowed size"


class ResumeParsingError(ResumeError):
    """Raised when readable text cannot be extracted from the resume."""

    status_code = 422
    default_detail = "The resume could not be parsed"


class ResumeNotFoundError(ResumeError):
    """Raised when a requested resume does not exist."""

    status_code = 404
    default_detail = "Resume not found"


class ResumeAccessDeniedError(ResumeError):
    """
    Raised when a user tries to access another user's resume.

    A 404 response avoids exposing whether another user's resource exists.
    """

    status_code = 404
    default_detail = "Resume not found"


class ResumeStorageError(ResumeError):
    """Raised for unexpected filesystem or database persistence failures."""

    status_code = 500
    default_detail = "The resume could not be stored"
