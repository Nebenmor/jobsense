# File: app/models/analysis.py
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import Integer, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Analysis(Base):
    """
    Represents one CV-to-job analysis result saved to the database.

    We store ONLY the analysis output — not the raw CV text or file.
    This is deliberate: data minimization means we never persist
    personally identifiable information beyond what's necessary.

    expires_at: set 30 days from creation. Expired records are filtered
    out in queries. A cleanup job can hard-delete them later.
    """
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_title: Mapped[str] = mapped_column(String, default="Untitled")
    match_score: Mapped[int] = mapped_column(Integer)
    matching_skills: Mapped[list] = mapped_column(JSON)
    missing_skills: Mapped[list] = mapped_column(JSON)
    suggestions: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=30)
    )