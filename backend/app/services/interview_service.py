import asyncio
import json
import logging
import re
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
            "Relevant experience, technical skills, projects, engineering "
            f"decisions, achievements, and responsibilities for a "
            f"{request.job_role} interview at "
            f"{request.experience_level} level"
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
            logger.warning(
                "Gemini returned %s questions, but %s were requested",
                result.total_questions,
                request.number_of_questions,
            )
            raise InvalidGeminiResponseError(
                "Gemini returned a different number of questions than requested"
            )

        return result

    @classmethod
    def _parse_response(
        cls,
        response: Any,
    ) -> InterviewQuestionsResponse:
        parsed = getattr(response, "parsed", None)

        try:
            if isinstance(parsed, InterviewQuestionsResponse):
                return parsed

            if parsed is not None:
                normalized = cls._normalize_response_data(parsed)
                return InterviewQuestionsResponse.model_validate(normalized)

            text = getattr(response, "text", None)

            if not text or not text.strip():
                raise InvalidGeminiResponseError(
                    "Gemini returned an empty response"
                )

            data = cls._extract_json(text)
            normalized = cls._normalize_response_data(data)

            return InterviewQuestionsResponse.model_validate(normalized)

        except InvalidGeminiResponseError:
            raise

        except (
            json.JSONDecodeError,
            ValidationError,
            TypeError,
            ValueError,
        ) as exc:
            logger.warning(
                "Gemini returned an invalid question response: %s",
                exc,
            )
            raise InvalidGeminiResponseError(
                "Gemini returned an invalid question response"
            ) from exc

    @staticmethod
    def _extract_json(text: str) -> Any:
        cleaned = text.strip()

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:
            object_start = cleaned.find("{")
            object_end = cleaned.rfind("}")

            if object_start != -1 and object_end > object_start:
                return json.loads(cleaned[object_start : object_end + 1])

            array_start = cleaned.find("[")
            array_end = cleaned.rfind("]")

            if array_start != -1 and array_end > array_start:
                return json.loads(cleaned[array_start : array_end + 1])

            raise

    @staticmethod
    def _normalize_response_data(data: Any) -> dict[str, list[str]]:
        if hasattr(data, "model_dump"):
            data = data.model_dump()

        expected_keys = (
            "technical_questions",
            "project_questions",
            "hr_questions",
            "coding_questions",
        )

        normalized: dict[str, list[str]] = {
            key: [] for key in expected_keys
        }

        if isinstance(data, dict):
            for key in expected_keys:
                value = data.get(key)

                if isinstance(value, list):
                    normalized[key].extend(
                        str(question).strip()
                        for question in value
                        if str(question).strip()
                    )

            nested_questions = data.get("questions")

            if isinstance(nested_questions, list):
                data = nested_questions
            else:
                return normalized

        if isinstance(data, list):
            for item in data:
                if hasattr(item, "model_dump"):
                    item = item.model_dump()

                if not isinstance(item, dict):
                    continue

                for key in expected_keys:
                    value = item.get(key)

                    if isinstance(value, list):
                        normalized[key].extend(
                            str(question).strip()
                            for question in value
                            if str(question).strip()
                        )

            return normalized

        raise ValueError(
            "Gemini response must be a JSON object or array"
        )