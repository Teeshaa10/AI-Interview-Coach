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

    CORS_ORIGINS: str = "http://localhost:5173"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS is stored as a comma-separated string because
        environment variables can only hold text, not native lists. This
        property parses it once into the list format FastAPI's
        CORSMiddleware actually expects."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Settings() reads and validates every environment variable when it's
    constructed. @lru_cache means that only happens once per process — the
    first call — and every later call (there will be many, since this is
    used as a FastAPI dependency on almost every route) returns the same
    cached object instead of re-reading the environment. This is the
    standard FastAPI settings pattern: configuration should never silently
    change mid-process.
    """
    return Settings()
