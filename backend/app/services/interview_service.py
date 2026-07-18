import asyncio
import logging
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.exceptions.interview import (
    EmptySemanticSearchResultsError,
    GeminiAPIError,
    GeminiConfigurationError,
    GeminiTimeoutError,
    InvalidGeminiResponseError,
)
from app.prompts.interview_prompt import (
    SYSTEM_INSTRUCTION,
    build_interview_prompt,
)
from app.schemas.interview import (
    InterviewQuestionRequest,
    InterviewQuestionsResponse,
)
from app.services.semantic_search_service import SemanticSearchService

logger = logging.getLogger(__name__)


class InterviewService:
    """Generates authenticated, resume-grounded interview questions."""

    def __init__(
        self,
        *,
        semantic_search_service: SemanticSearchService,
        gemini_client: genai.Client | None,
        model_name: str,
        search_top_k: int,
        timeout_seconds: float,
    ) -> None:
        self._semantic_search_service = semantic_search_service
        self._gemini_client = gemini_client
        self._model_name = model_name
        self._search_top_k = search_top_k
        self._timeout_seconds = timeout_seconds

    async def generate_questions(
        self,
        *,
        user_id: str,
        request: InterviewQuestionRequest,
    ) -> InterviewQuestionsResponse:

        if self._gemini_client is None:
            raise GeminiConfigurationError()

        search_query = (
            f"Relevant experience, technical skills, projects, engineering decisions, "
            f"achievements, and responsibilities for a "
            f"{request.job_role} interview at {request.experience_level} level"
        )

        chunks = await self._semantic_search_service.search(
            query=search_query,
            user_id=user_id,
            resume_id=request.resume_id,
            top_k=self._search_top_k,
            min_similarity=0.0,
        )

        if not chunks:
            raise EmptySemanticSearchResultsError()

        prompt = build_interview_prompt(
            job_role=request.job_role,
            experience_level=request.experience_level,
            number_of_questions=request.number_of_questions,
            chunks=chunks,
        )

        # IMPORTANT:
        # Do NOT pass response_schema.
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.35,
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
            logger.warning(
                "Gemini request timed out for resume %s",
                request.resume_id,
            )
            raise GeminiTimeoutError() from exc

        except errors.APIError as exc:
            logger.exception(
                "Gemini API request failed for resume %s",
                request.resume_id,
            )
            raise GeminiAPIError() from exc

        except Exception as exc:
            logger.exception(
                "Unexpected Gemini failure for resume %s",
                request.resume_id,
            )
            raise GeminiAPIError() from exc

        result = self._parse_response(response)

        if result.total_questions != request.number_of_questions:
            raise InvalidGeminiResponseError(
                "Gemini returned a different number of questions than requested"
            )

        return result

    @staticmethod
    def _parse_response(response: Any) -> InterviewQuestionsResponse:

        parsed = getattr(response, "parsed", None)

        try:
            if isinstance(parsed, InterviewQuestionsResponse):
                return parsed

            if parsed is not None:
                return InterviewQuestionsResponse.model_validate(parsed)

            text = getattr(response, "text", None)

            if not text or not text.strip():
                raise InvalidGeminiResponseError(
                    "Gemini returned an empty response"
                )

            return InterviewQuestionsResponse.model_validate_json(text)

        except ValidationError as exc:
            logger.warning(
                "Gemini returned invalid JSON: %s",
                exc,
            )
            raise InvalidGeminiResponseError() from exc