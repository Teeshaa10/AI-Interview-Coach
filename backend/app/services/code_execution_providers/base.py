from abc import ABC, abstractmethod

from app.schemas.coding_interview import CodingTestCase, TestExecutionResult


class CodeExecutionProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def supported_languages(self) -> list[str]: ...

    @abstractmethod
    async def execute(self, *, source_code: str, language: str, test_cases: list[CodingTestCase]) -> list[TestExecutionResult]: ...
