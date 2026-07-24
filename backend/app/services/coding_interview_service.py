import asyncio
import json
import logging
import re
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.exceptions.coding import (
    CodingQuestionNotFoundError,
    MalformedCodingQuestionError,
    SourceCodeTooLargeError,
    UnsupportedLanguageError,
)
from app.repositories.coding_interview_repository import (
    CodingInterviewRepository,
)
from app.schemas.coding_interview import (
    CodingInterviewSession,
    CodingInterviewStartRequest,
    CodingQuestion,
    CodingSubmission,
    CodingSubmitRequest,
)
from app.services.code_execution_service import CodeExecutionService

logger = logging.getLogger(__name__)


class CodingInterviewService:
    def __init__(
        self,
        *,
        repository: CodingInterviewRepository,
        execution_service: CodeExecutionService,
        gemini_client: genai.Client | None,
        model_name: str,
        timeout_seconds: float,
        max_source_length: int,
    ):
        self.repository = repository
        self.execution_service = execution_service
        self.gemini_client = gemini_client
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.max_source_length = max_source_length

    async def generate_questions(
        self,
        request: CodingInterviewStartRequest,
    ) -> list[CodingQuestion]:
        if self.gemini_client is None:
            raise MalformedCodingQuestionError()

        topics = (
            ", ".join(request.topics)
            if request.topics
            else "arrays, strings, hashing, and problem solving"
        )

        prompt = f"""
Generate exactly {request.number_of_questions} coding interview questions.

Candidate role: {request.role}
Experience level: {request.experience_level}
Difficulty: {request.difficulty}
Preferred language: {request.language}
Topics: {topics}

Return only valid JSON in this exact structure:

{{
  "questions": [
    {{
      "title": "Question title",
      "problem_statement": "Complete problem statement",
      "difficulty": "{request.difficulty}",
      "topics": ["arrays"],
      "constraints": ["1 <= n <= 100000"],
      "examples": [
        {{
          "input": "5\\n1 2 3 4 5",
          "output": "15",
          "explanation": "Explanation"
        }}
      ],
      "function_signature": "long long solve(vector<int>& nums)",
      "starter_code": {{
        "cpp": "#include <bits/stdc++.h>\\nusing namespace std;\\n\\nint main() {{\\n    return 0;\\n}}",
        "python": "",
        "java": "",
        "javascript": ""
      }},
      "visible_test_cases": [
        {{
          "input": "5\\n1 2 3 4 5",
          "expected_output": "15"
        }},
        {{
          "input": "3\\n-1 0 1",
          "expected_output": "0"
        }}
      ],
      "hidden_test_cases": [
        {{
          "input": "1\\n10",
          "expected_output": "10"
        }},
        {{
          "input": "4\\n2 2 2 2",
          "expected_output": "8"
        }}
      ],
      "expected_complexity": {{
        "time": "O(n)",
        "space": "O(1)"
      }}
    }}
  ]
}}

Rules:

1. Return exactly {request.number_of_questions} questions.
2. Every question must contain all fields shown above.
3. Use stdin/stdout compatible test cases.
4. Every test case must contain input and expected_output.
5. Include at least two visible and two hidden test cases.
6. Do not include Markdown code fences.
7. Do not include explanatory text outside the JSON.
"""

        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        )

        try:
            response = await asyncio.wait_for(
                self.gemini_client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                ),
                timeout=self.timeout_seconds,
            )

        except asyncio.TimeoutError as exc:
            logger.warning("Gemini coding question request timed out")
            raise MalformedCodingQuestionError() from exc

        except errors.APIError as exc:
            logger.exception("Gemini coding question API request failed")
            raise MalformedCodingQuestionError() from exc

        except Exception as exc:
            logger.exception(
                "Unexpected Gemini coding question generation failure"
            )
            raise MalformedCodingQuestionError() from exc

        raw_text = getattr(response, "text", None) or ""

        logger.info(
            "Raw Gemini coding question response: %s",
            raw_text,
        )

        try:
            data = self._extract_json(raw_text)
            items = self._extract_question_list(data)

            questions: list[CodingQuestion] = []

            for index, item in enumerate(items, start=1):
                normalized = self._normalize_question(
                    item=item,
                    index=index,
                    default_difficulty=request.difficulty,
                    preferred_language=request.language,
                )

                questions.append(
                    CodingQuestion.model_validate(normalized)
                )

            if len(questions) != request.number_of_questions:
                raise ValueError(
                    f"Expected {request.number_of_questions} questions, "
                    f"but Gemini returned {len(questions)}"
                )

            return questions

        except (
            ValidationError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            logger.warning(
                "Gemini returned malformed coding questions. "
                "Parsing error: %s. Raw response: %s",
                exc,
                raw_text,
            )
            raise MalformedCodingQuestionError() from exc

    async def run_code(
        self,
        *,
        session: CodingInterviewSession,
        request: "CodingRunRequest",
    ) -> "CodingRunResponse":
        """Executes code against only the question's visible test cases,
        without persisting anything or computing a score. This backs the
        'Run Code' button, kept deliberately separate from submit() so
        candidates can iterate without spending a graded attempt."""

        if len(request.source_code) > self.max_source_length:
            raise SourceCodeTooLargeError()

        language = request.language.lower().strip()

        if language not in self.execution_service.supported_languages:
            if not self.execution_service.supported_languages:
                from app.exceptions.coding import ExecutionProviderUnavailableError

                raise ExecutionProviderUnavailableError()
            raise UnsupportedLanguageError(language)

        question = next(
            (q for q in session.questions if q.question_number == request.question_number),
            None,
        )
        if question is None:
            raise CodingQuestionNotFoundError()

        results = await self.execution_service.execute(
            source_code=request.source_code,
            language=language,
            test_cases=question.visible_test_cases,
        )

        passed = sum(1 for result in results if result.passed)

        from app.schemas.coding_interview import CodingRunResponse

        return CodingRunResponse(test_results=results, tests_passed=passed, tests_total=len(results))

    async def submit(
        self,
        *,
        session: CodingInterviewSession,
        request: CodingSubmitRequest,
        user_id: str,
    ) -> CodingSubmission:
        if len(request.source_code) > self.max_source_length:
            raise SourceCodeTooLargeError()

        language = request.language.lower().strip()

        if language not in self.execution_service.supported_languages:
            if not self.execution_service.supported_languages:
                from app.exceptions.coding import (
                    ExecutionProviderUnavailableError,
                )

                raise ExecutionProviderUnavailableError()

            raise UnsupportedLanguageError(language)

        question = next(
            (
                q
                for q in session.questions
                if q.question_number == request.question_number
            ),
            None,
        )

        if question is None:
            raise CodingQuestionNotFoundError()

        all_tests = [
            *question.visible_test_cases,
            *question.hidden_test_cases,
        ]

        results = await self.execution_service.execute(
            source_code=request.source_code,
            language=language,
            test_cases=all_tests,
        )

        passed = sum(1 for result in results if result.passed)
        total = len(results)

        correctness = (
            round((passed / total) * 6.0, 2)
            if total
            else 0.0
        )

        quality = self._quality_score(request.source_code)

        complexity = (
            1.5
            if request.explanation.strip()
            else 0.5
        )

        explanation = (
            1.0
            if len(request.explanation.strip()) >= 30
            else 0.5
            if request.explanation.strip()
            else 0.0
        )

        overall = round(
            min(
                10.0,
                correctness
                + quality
                + complexity
                + explanation,
            ),
            2,
        )

        feedback: list[str] = []

        if passed == total and total:
            feedback.append(
                "All visible and hidden tests passed."
            )
        else:
            feedback.append(
                f"Passed {passed} of {total} tests."
            )

        if not request.explanation.strip():
            feedback.append(
                "Add an explanation of the approach and complexity."
            )

        submission = CodingSubmission(
            session_id=session.id or "",
            user_id=user_id,
            question_number=request.question_number,
            language=language,
            source_code=request.source_code,
            explanation=request.explanation,
            test_results=results,
            tests_passed=passed,
            tests_total=total,
            correctness_score=correctness,
            quality_score=quality,
            complexity_score=complexity,
            explanation_score=explanation,
            overall_score=overall,
            feedback=feedback,
        )

        submission.id = await self.repository.create_submission(
            submission
        )

        return submission

    @staticmethod
    def _quality_score(source: str) -> float:
        score = 0.5

        if len(source.splitlines()) >= 5:
            score += 0.25

        if any(
            token in source
            for token in (
                "function",
                "def ",
                "class ",
                "int main",
            )
        ):
            score += 0.25

        return round(min(1.5, score), 2)

    @staticmethod
    def _extract_json(text: str) -> Any:
        if not text or not text.strip():
            raise ValueError(
                "Gemini returned an empty response"
            )

        cleaned = text.strip()

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:
            object_start = cleaned.find("{")
            object_end = cleaned.rfind("}")

            if object_start != -1 and object_end > object_start:
                object_text = cleaned[
                    object_start : object_end + 1
                ]

                try:
                    return json.loads(object_text)
                except json.JSONDecodeError:
                    pass

            array_start = cleaned.find("[")
            array_end = cleaned.rfind("]")

            if array_start != -1 and array_end > array_start:
                array_text = cleaned[
                    array_start : array_end + 1
                ]
                return json.loads(array_text)

            raise

    @staticmethod
    def _extract_question_list(data: Any) -> list[Any]:
        if isinstance(data, list):
            return data

        if not isinstance(data, dict):
            raise ValueError(
                "Gemini response must be an object or array"
            )

        possible_keys = (
            "questions",
            "coding_questions",
            "interview_questions",
            "generated_questions",
            "items",
        )

        for key in possible_keys:
            value = data.get(key)

            if isinstance(value, list):
                return value

        if all(
            key in data
            for key in (
                "title",
                "problem_statement",
            )
        ):
            return [data]

        raise ValueError(
            "Gemini response does not contain a question list"
        )

    @classmethod
    def _normalize_question(
        cls,
        *,
        item: Any,
        index: int,
        default_difficulty: str,
        preferred_language: str,
    ) -> dict[str, Any]:
        if hasattr(item, "model_dump"):
            item = item.model_dump()

        if not isinstance(item, dict):
            raise ValueError(
                f"Question {index} must be an object"
            )

        normalized = dict(item)

        normalized["question_number"] = index

        normalized["title"] = cls._first_string(
            normalized,
            (
                "title",
                "question_title",
                "name",
            ),
            default=f"Coding Question {index}",
        )

        normalized["problem_statement"] = cls._first_string(
            normalized,
            (
                "problem_statement",
                "description",
                "problem",
                "question",
                "statement",
            ),
        )

        if not normalized["problem_statement"]:
            raise ValueError(
                f"Question {index} is missing problem_statement"
            )

        difficulty = str(
            normalized.get(
                "difficulty",
                default_difficulty,
            )
        ).lower().strip()

        if difficulty not in {
            "easy",
            "medium",
            "hard",
        }:
            difficulty = default_difficulty

        normalized["difficulty"] = difficulty

        normalized["topics"] = cls._string_list(
            normalized.get("topics")
            or normalized.get("tags")
        )

        normalized["constraints"] = cls._string_list(
            normalized.get("constraints")
        )

        normalized["examples"] = cls._normalize_examples(
            normalized.get("examples")
            or normalized.get("sample_cases")
            or normalized.get("sample_test_cases")
        )

        normalized["function_signature"] = cls._first_string(
            normalized,
            (
                "function_signature",
                "signature",
                "method_signature",
            ),
            default="",
        )

        normalized["starter_code"] = cls._normalize_starter_code(
            normalized.get("starter_code"),
            preferred_language,
        )

        visible = (
            normalized.get("visible_test_cases")
            or normalized.get("public_test_cases")
            or normalized.get("sample_tests")
        )

        hidden = (
            normalized.get("hidden_test_cases")
            or normalized.get("private_test_cases")
        )

        combined_tests = normalized.get("test_cases")

        if not visible and isinstance(combined_tests, list):
            midpoint = max(1, len(combined_tests) // 2)
            visible = combined_tests[:midpoint]

            if not hidden:
                hidden = combined_tests[midpoint:]

        normalized["visible_test_cases"] = (
            cls._normalize_test_cases(visible)
        )

        normalized["hidden_test_cases"] = (
            cls._normalize_test_cases(hidden)
        )

        normalized["expected_complexity"] = (
            cls._normalize_complexity(
                normalized.get("expected_complexity")
                or normalized.get("complexity")
            )
        )

        return normalized

    @staticmethod
    def _first_string(
        data: dict[str, Any],
        keys: tuple[str, ...],
        default: str = "",
    ) -> str:
        for key in keys:
            value = data.get(key)

            if value is not None:
                text = str(value).strip()

                if text:
                    return text

        return default

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        if isinstance(value, list):
            return [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

        return [str(value).strip()]

    @staticmethod
    def _normalize_examples(
        value: Any,
    ) -> list[dict[str, str]]:
        if value is None:
            return []

        if not isinstance(value, list):
            value = [value]

        examples: list[dict[str, str]] = []

        for item in value:
            if not isinstance(item, dict):
                continue

            input_value = item.get(
                "input",
                item.get("sample_input", ""),
            )

            output_value = item.get(
                "output",
                item.get(
                    "expected_output",
                    item.get("sample_output", ""),
                ),
            )

            examples.append(
                {
                    "input": str(input_value),
                    "output": str(output_value),
                    "explanation": str(
                        item.get("explanation", "")
                    ),
                }
            )

        return examples

    @staticmethod
    def _normalize_test_cases(
        value: Any,
    ) -> list[dict[str, str]]:
        if value is None:
            return []

        if not isinstance(value, list):
            value = [value]

        test_cases: list[dict[str, str]] = []

        for item in value:
            if not isinstance(item, dict):
                continue

            input_value = item.get(
                "input",
                item.get(
                    "stdin",
                    item.get("input_data", ""),
                ),
            )

            output_value = item.get(
                "expected_output",
                item.get(
                    "output",
                    item.get(
                        "stdout",
                        item.get("expected", ""),
                    ),
                ),
            )

            test_cases.append(
                {
                    "input": str(input_value),
                    "expected_output": str(output_value),
                }
            )

        return test_cases

    @staticmethod
    def _normalize_starter_code(
        value: Any,
        preferred_language: str,
    ) -> dict[str, str]:
        if isinstance(value, dict):
            return {
                str(key).lower().strip(): str(code)
                for key, code in value.items()
                if code is not None
            }

        if isinstance(value, str):
            return {
                preferred_language.lower().strip(): value
            }

        if isinstance(value, list):
            result: dict[str, str] = {}

            for item in value:
                if not isinstance(item, dict):
                    continue

                language = item.get(
                    "language",
                    item.get("name"),
                )

                code = item.get(
                    "code",
                    item.get("starter_code"),
                )

                if language and code is not None:
                    result[str(language).lower().strip()] = str(
                        code
                    )

            return result

        return {}

    @staticmethod
    def _normalize_complexity(
        value: Any,
    ) -> dict[str, str]:
        if isinstance(value, dict):
            return {
                "time": str(
                    value.get(
                        "time",
                        value.get(
                            "time_complexity",
                            "",
                        ),
                    )
                ),
                "space": str(
                    value.get(
                        "space",
                        value.get(
                            "space_complexity",
                            "",
                        ),
                    )
                ),
            }

        if isinstance(value, str):
            time_match = re.search(
                r"time[^:]*:\s*([^,\n;]+)",
                value,
                flags=re.IGNORECASE,
            )

            space_match = re.search(
                r"space[^:]*:\s*([^,\n;]+)",
                value,
                flags=re.IGNORECASE,
            )

            return {
                "time": (
                    time_match.group(1).strip()
                    if time_match
                    else value.strip()
                ),
                "space": (
                    space_match.group(1).strip()
                    if space_match
                    else ""
                ),
            }

        return {
            "time": "",
            "space": "",
        }