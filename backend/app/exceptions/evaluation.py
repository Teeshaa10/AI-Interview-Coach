class EvaluationError(Exception):
    status_code = 500
    default_detail = "Interview answer could not be evaluated"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class EvaluationConfigurationError(EvaluationError):
    status_code = 503
    default_detail = "Gemini is not configured on the server"


class EvaluationAPIError(EvaluationError):
    status_code = 502
    default_detail = "Gemini could not evaluate the interview answer"


class EvaluationTimeoutError(EvaluationError):
    status_code = 504
    default_detail = "Gemini did not respond before the request timed out"


class InvalidEvaluationResponseError(EvaluationError):
    status_code = 502
    default_detail = "Gemini returned an invalid evaluation response"