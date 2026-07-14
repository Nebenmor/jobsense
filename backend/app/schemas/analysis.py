# File: app/schemas/analysis.py
from pydantic import BaseModel, Field
from datetime import datetime


class AnalysisResponse(BaseModel):
    """
    Returned immediately after analysis — the full result.
    Also the shape we expect from the Groq/Llama response.
    """
    job_title: str = Field(default="Untitled")
    match_score: int = Field(ge=0, le=100)
    matching_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]


class AnalysisSaved(AnalysisResponse):
    """
    Extends AnalysisResponse with database fields.
    Returned when fetching saved analyses — includes id and timestamps.
    """
    id: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True  # allows creating from SQLAlchemy model instances


class AnalysisSummary(BaseModel):
    """
    Lightweight version for the list endpoint GET /api/v1/analyses.
    Only returns what's needed for a list view — not the full skills/suggestions.
    """
    id: str
    job_title: str
    match_score: int
    created_at: datetime

    class Config:
        from_attributes = True