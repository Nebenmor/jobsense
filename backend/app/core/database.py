# File: app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# The engine manages the connection pool to PostgreSQL.
# pool_pre_ping=True checks connections are alive before using them —
# prevents errors from stale connections after idle periods.
engine = create_async_engine(settings.database_url, pool_pre_ping=True)

# Session factory — call this to get a database session.
# expire_on_commit=False means we can still access model attributes
# after committing without hitting the DB again.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Every model inherits from this — it's how SQLAlchemy knows
    which classes represent database tables.
    """
    pass


async def get_db():
    """
    FastAPI dependency that provides a database session per request.
    The 'async with' ensures the session is always closed after the
    request completes — even if an exception is raised.
    """
    async with AsyncSessionLocal() as session:
        yield session