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

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT_SECONDS: float = 45.0
    INTERVIEW_SEARCH_TOP_K: int = 8

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ==========================
    # Module 6 - Voice Interview
    # ==========================

    WHISPER_MODEL_NAME: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    VOICE_AUDIO_DIR: str = "./voice_audio"

    VOICE_MAX_AUDIO_SIZE_MB: int = 25

    TTS_DEFAULT_VOICE: str = "en-US-AriaNeural"

    TTS_MAX_TEXT_LENGTH: int = 3000

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