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

    class Config:
        env_file = ".env"


settings = Settings()