from app.exceptions.coding import ExecutionProviderUnavailableError, UnsupportedLanguageError
from app.schemas.coding_interview import CodingTestCase, TestExecutionResult
from app.services.code_execution_providers.base import CodeExecutionProvider


class CodeExecutionService:
    def __init__(self, provider: CodeExecutionProvider | None):
        self.provider = provider

    @property
    def provider_name(self) -> str:
        return self.provider.name if self.provider else "unconfigured"

    @property
    def supported_languages(self) -> list[str]:
        return self.provider.supported_languages if self.provider else []

    async def execute(self, *, source_code: str, language: str, test_cases: list[CodingTestCase]) -> list[TestExecutionResult]:
        if self.provider is None:
            raise ExecutionProviderUnavailableError()
        language = language.lower().strip()
        if language not in self.provider.supported_languages:
            raise UnsupportedLanguageError(language)
        return await self.provider.execute(source_code=source_code, language=language, test_cases=test_cases)
