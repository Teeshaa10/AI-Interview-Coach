import json
import re

from app.prompts.resume_analysis_prompt import (
    RESUME_ANALYSIS_PROMPT,
    RESUME_ANALYSIS_SYSTEM_INSTRUCTION,
)
from app.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)
from app.schemas.resume_analysis import ResumeAnalysisResult


class ResumeAnalysisService:
    def __init__(
        self,
        analysis_repository: ResumeAnalysisRepository,
        resume_repository,
        gemini_client,
        model_name: str,
    ):
        self.analysis_repository = analysis_repository
        self.resume_repository = resume_repository
        self.gemini_client = gemini_client
        self.model_name = model_name

    async def analyze_resume(
        self,
        user_id: str,
        resume_id: str,
        target_role: str,
    ) -> dict:
        resume = await self.resume_repository.get_resume_by_id(
            resume_id
        )

        if resume is None or resume.user_id != user_id:
            raise ValueError("Resume not found")

        resume_text = self._extract_resume_text(resume)

        prompt = RESUME_ANALYSIS_PROMPT.format(
            target_role=target_role,
            resume_text=resume_text,
        )

        response = self.gemini_client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "system_instruction": RESUME_ANALYSIS_SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
            },
        )

        raw_text = response.text or ""

        parsed_data = self._parse_json_response(raw_text)

        validated_result = ResumeAnalysisResult.model_validate(
            parsed_data
        )

        analysis_data = {
            "user_id": user_id,
            "resume_id": resume_id,
            "target_role": target_role,
            **validated_result.model_dump(),
        }

        return await self.analysis_repository.create(
            analysis_data
        )

    async def get_analysis(
        self,
        analysis_id: str,
        user_id: str,
    ) -> dict | None:
        return await self.analysis_repository.get_by_id(
            analysis_id=analysis_id,
            user_id=user_id,
        )

    async def get_latest_analysis(
        self,
        resume_id: str,
        user_id: str,
    ) -> dict | None:
        return await self.analysis_repository.get_latest_by_resume(
            resume_id=resume_id,
            user_id=user_id,
        )

    async def get_history(
        self,
        user_id: str,
    ) -> list[dict]:
        return await self.analysis_repository.get_history(
            user_id=user_id
        )

    async def delete_analysis(
        self,
        analysis_id: str,
        user_id: str,
    ) -> bool:
        return await self.analysis_repository.delete(
            analysis_id=analysis_id,
            user_id=user_id,
        )

    @staticmethod
    def _extract_resume_text(resume) -> str:
        resume_text = resume.extracted_text.strip()

        if not resume_text:
            raise ValueError("Resume text is empty")

        return resume_text

    @staticmethod
    def _parse_json_response(
        raw_text: str,
    ) -> dict:
        cleaned = raw_text.strip()

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
            match = re.search(
                r"\{.*\}",
                cleaned,
                flags=re.DOTALL,
            )

            if not match:
                raise ValueError(
                    "Gemini returned invalid JSON"
                )

            try:
                return json.loads(
                    match.group(0)
                )
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Gemini returned invalid JSON"
                ) from exc