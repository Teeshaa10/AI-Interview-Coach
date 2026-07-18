from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration object for the backend.

    Every value here is read from environment variables (or a local .env
    file during development). Nothing else in the app should call
    os.environ directly — this class is the single source of truth for
    configuration. That makes every tunable value visible in one place, and
    lets us switch environments (dev / staging / prod) purely by changing
    environment variables, never code.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    MONGODB_URI: str
    MONGODB_DB_NAME: str = "interview_coach"

    CHROMA_PERSIST_DIR: str = "./chroma_data"
    # CHROMA_COLLECTION_NAME: str = "resume_embeddings"
    CHROMA_COLLECTION_NAME: str = "resume_chunks"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_CHUNK_SIZE: int = 500
    EMBEDDING_CHUNK_OVERLAP: int = 100

    # Google Gemini configuration for resume-grounded interview generation.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT_SECONDS: float = 45.0
    INTERVIEW_SEARCH_TOP_K: int = 8

    CORS_ORIGINS: str = "http://localhost:5173"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        """
        CORS_ORIGINS is stored as a comma-separated string because
        environment variables can only hold text, not native lists.
        This property converts it into the list format expected by
        FastAPI's CORSMiddleware.
        """
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Settings() reads and validates every environment variable only once.
    Subsequent calls return the same cached object.
    """
    return Settings()