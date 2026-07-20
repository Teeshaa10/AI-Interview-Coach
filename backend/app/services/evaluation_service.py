import asyncio
import logging
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.exceptions.evaluation import (
    EvaluationAPIError,
    EvaluationConfigurationError,
    EvaluationTimeoutError,
    InvalidEvaluationResponseError,
)
from app.prompts.evaluation_prompt import (
    EVALUATION_PROMPT,
    SYSTEM_INSTRUCTION,
)
from app.schemas.interview_evaluation import (
    InterviewEvaluationResponse,
)

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Uses Gemini to evaluate a candidate's answer.
    """

    def __init__(
        self,
        *,
        gemini_client: genai.Client | None,
        model_name: str,
        timeout_seconds: float,
    ) -> None:
        self._gemini_client = gemini_client
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds

    async def evaluate_answer(
        self,
        *,
        question: str,
        answer: str,
        resume_context: str,
        job_role: str,
        experience_level: str,
    ) -> InterviewEvaluationResponse:

        if self._gemini_client is None:
            raise EvaluationConfigurationError()

        prompt = EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            resume_context=resume_context,
            job_role=job_role,
            experience_level=experience_level,
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            response_mime_type="application/json",
        )

        try:
            response = await asyncio.wait_for(
                self._gemini_client.aio.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                ),
                timeout=self._timeout_seconds,
            )

        except asyncio.TimeoutError as exc:
            logger.exception("Gemini evaluation timeout")
            raise EvaluationTimeoutError() from exc

        except errors.APIError as exc:
            logger.exception("Gemini evaluation API error")
            raise EvaluationAPIError() from exc

        except Exception as exc:
            logger.exception("Unexpected Gemini evaluation error")
            raise EvaluationAPIError() from exc

        return self._parse_response(response)

    @staticmethod
    def _parse_response(
        response: Any,
    ) -> InterviewEvaluationResponse:

        parsed = getattr(response, "parsed", None)

        try:

            if isinstance(parsed, InterviewEvaluationResponse):
                return parsed

            if parsed is not None:
                return InterviewEvaluationResponse.model_validate(parsed)

            text = getattr(response, "text", None)

            if not text or not text.strip():
                raise InvalidEvaluationResponseError(
                    "Gemini returned an empty response."
                )

            return InterviewEvaluationResponse.model_validate_json(text)

        except ValidationError as exc:
            logger.exception(
                "Invalid evaluation response received from Gemini."
            )
            raise InvalidEvaluationResponseError() from exc