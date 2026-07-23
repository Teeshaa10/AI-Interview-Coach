import asyncio
import base64

import httpx

from app.exceptions.coding import ExecutionFailureError
from app.schemas.coding_interview import CodingTestCase, TestExecutionResult
from app.services.code_execution_providers.base import CodeExecutionProvider


class Judge0Provider(CodeExecutionProvider):
    LANGUAGE_IDS = {"cpp": 54, "python": 71, "java": 62, "javascript": 63}

    def __init__(self, base_url: str, api_key: str, api_host: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_host = api_host
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "judge0"

    @property
    def supported_languages(self) -> list[str]:
        return list(self.LANGUAGE_IDS)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key
        if self.api_host:
            headers["X-RapidAPI-Host"] = self.api_host
        return headers

    @staticmethod
    def _decode(value: str | None) -> str:
        if not value:
            return ""
        try:
            return base64.b64decode(value).decode("utf-8", errors="replace").strip()
        except Exception:
            return value.strip()

    async def execute(self, *, source_code: str, language: str, test_cases: list[CodingTestCase]) -> list[TestExecutionResult]:
        results = []
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for case in test_cases:
                try:
                    response = await client.post(
                        f"{self.base_url}/submissions?base64_encoded=true&wait=true",
                        headers=self._headers(),
                        json={
                            "language_id": self.LANGUAGE_IDS[language],
                            "source_code": base64.b64encode(source_code.encode()).decode(),
                            "stdin": base64.b64encode(case.input.encode()).decode(),
                            "expected_output": base64.b64encode(case.expected_output.encode()).decode(),
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    output = self._decode(data.get("stdout"))
                    stderr = self._decode(data.get("stderr") or data.get("compile_output"))
                    results.append(TestExecutionResult(
                        input=case.input,
                        expected_output=case.expected_output,
                        actual_output=output,
                        passed=not stderr and output == case.expected_output.strip(),
                        stderr=stderr,
                        execution_time=float(data["time"]) if data.get("time") else None,
                    ))
                except (httpx.HTTPError, ValueError) as exc:
                    raise ExecutionFailureError(str(exc)) from exc
        return results
