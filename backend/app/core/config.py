# File: app/core/config.py
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from pydantic_settings import BaseSettings

# libpq-style URL params (Neon includes these in its connection string).
# asyncpg does not accept them as URL query args, so we strip them
# and translate sslmode into asyncpg's `ssl` connect argument instead.
_LIBPQ_ONLY_PARAMS = {"sslmode", "channel_binding"}


class Settings(BaseSettings):
    """
    Centralized app configuration.
    Values are loaded from a .env file (never committed to git)
    or from real environment variables in production.
    """
    groq_api_key: str
    database_url: str
    max_cv_size_mb: int = 5
    groq_model: str = "openai/gpt-oss-120b"

    @property
    def async_database_url(self) -> str:
        """
        Accepts a standard postgres:// or postgresql:// URL (Neon, Render, local)
        and returns a postgresql+asyncpg:// URL that asyncpg can actually use:
        correct driver prefix, and no sslmode/channel_binding query params.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        parts = urlsplit(url)
        query = [
            (k, v) for k, v in parse_qsl(parts.query)
            if k not in _LIBPQ_ONLY_PARAMS
        ]
        return urlunsplit(parts._replace(query=urlencode(query)))

    @property
    def db_connect_args(self) -> dict:
        """
        Extra arguments passed to asyncpg.
        - ssl: turned on when the URL asks for it (Neon URLs end in ?sslmode=require).
          Local URLs without sslmode stay unencrypted, as before.
        - statement_cache_size=0: makes the app work with Neon's pooled
          (-pooler) connection string too, since PgBouncer in transaction
          mode can't reuse cached prepared statements.
        """
        params = dict(parse_qsl(urlsplit(self.database_url).query))
        args: dict = {"statement_cache_size": 0}
        if params.get("sslmode") in {"require", "verify-ca", "verify-full"}:
            args["ssl"] = "require"
        return args

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()