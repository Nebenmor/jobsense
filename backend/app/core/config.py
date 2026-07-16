# File: app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Centralized app configuration.
    Values are loaded from a .env file (never committed to git)
    or from real environment variables in production.
    """
    groq_api_key: str
    database_url: str
    max_cv_size_mb: int = 5
    groq_model: str = "llama-3.3-70b-versatile"

    @property
    def async_database_url(self) -> str:
        """
        Render provides a standard postgres:// URL.
        SQLAlchemy asyncpg requires postgresql+asyncpg://.
        This property ensures the correct driver prefix is always used
        regardless of which format the environment variable contains.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()