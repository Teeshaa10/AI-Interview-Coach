import httpx

from app.exceptions.coding import ExecutionFailureError
from app.schemas.coding_interview import (
    CodingTestCase,
    TestExecutionResult,
)
from app.services.code_execution_providers.base import (
    CodeExecutionProvider,
)


class PistonProvider(CodeExecutionProvider):
    VERSIONS = {
        "python": "3.10.0",
        "cpp": "10.2.0",
        "java": "15.0.2",
        "javascript": "18.15.0",
    }

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "piston"

    @property
    def supported_languages(self) -> list[str]:
        return list(self.VERSIONS)

    async def execute(
        self,
        *,
        source_code: str,
        language: str,
        test_cases: list[CodingTestCase],
    ) -> list[TestExecutionResult]:
        results: list[TestExecutionResult] = []

        execute_url = f"{self.base_url}/execute"

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
        ) as client:
            for case in test_cases:
                try:
                    response = await client.post(
                        execute_url,
                        json={
                            "language": language,
                            "version": self.VERSIONS[language],
                            "files": [
                                {
                                    "content": source_code,
                                }
                            ],
                            "stdin": case.input,
                        },
                    )

                    response.raise_for_status()
                    data = response.json()

                    run = data.get("run", {})

                    output = str(
                        run.get("stdout", "")
                    ).strip()

                    stderr = str(
                        run.get("stderr", "")
                    ).strip()

                    compile_data = data.get("compile", {})

                    compile_stderr = str(
                        compile_data.get("stderr", "")
                    ).strip()

                    combined_stderr = "\n".join(
                        error
                        for error in (
                            compile_stderr,
                            stderr,
                        )
                        if error
                    )

                    results.append(
                        TestExecutionResult(
                            input=case.input,
                            expected_output=case.expected_output,
                            actual_output=output,
                            passed=(
                                not combined_stderr
                                and output
                                == case.expected_output.strip()
                            ),
                            stderr=combined_stderr,
                            execution_time=run.get("wall_time"),
                        )
                    )

                except httpx.HTTPStatusError as exc:
                    response_text = exc.response.text

                    raise ExecutionFailureError(
                        f"Piston returned HTTP "
                        f"{exc.response.status_code}: "
                        f"{response_text}"
                    ) from exc

                except httpx.RequestError as exc:
                    raise ExecutionFailureError(
                        f"Could not connect to Piston: {exc}"
                    ) from exc

                except (ValueError, KeyError) as exc:
                    raise ExecutionFailureError(
                        f"Invalid Piston response: {exc}"
                    ) from exc

        return results