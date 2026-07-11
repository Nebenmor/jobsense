# File: app/schemas/analysis.py
from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """
    This is the exact shape of data we return to the frontend
    after analyzing a CV against a job description.
    It also doubles as the shape we expect Gemini to return —
    using one schema for both keeps things consistent.
    """
    job_title: str = Field(default="Untitled")
    match_score: int = Field(ge=0, le=100)
    matching_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]