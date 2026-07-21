from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the backend application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    MONGODB_URI: str
    MONGODB_DB_NAME: str = "interview_coach"

    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "resume_chunks"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_CHUNK_SIZE: int = 500
    EMBEDDING_CHUNK_OVERLAP: int = 100

    # Google Gemini configuration. Put the real key in backend/.env.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT_SECONDS: float = 45.0
    INTERVIEW_SEARCH_TOP_K: int = 8

    # Module 6: local Whisper speech-to-text and Edge text-to-speech.
    WHISPER_MODEL_NAME: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    TTS_DEFAULT_VOICE: str = "en-US-AriaNeural"
    VOICE_AUDIO_DIR: str = "./voice_audio"
    VOICE_MAX_AUDIO_SIZE_MB: int = 25


    # Module 7: report generation and analytics.
    REPORT_AI_SUMMARY_ENABLED: bool = True

    # Module 8: remote sandboxed code execution.
    CODE_EXECUTION_PROVIDER: str = "judge0"
    JUDGE0_BASE_URL: str = ""
    JUDGE0_API_KEY: str = ""
    JUDGE0_API_HOST: str = ""
    PISTON_BASE_URL: str = ""
    CODE_EXECUTION_TIMEOUT_SECONDS: float = 15.0
    CODE_MAX_SOURCE_LENGTH: int = 50000
    CODING_MAX_QUESTIONS: int = 5

    CORS_ORIGINS: str = "http://localhost:5173"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()