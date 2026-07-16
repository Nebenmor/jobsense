# File: app/routes/analyze.py
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.analysis import Analysis
from app.services.pdf_service import extract_text_from_pdf
from app.services.groq_service import analyze_cv_match
from app.schemas.analysis import AnalysisResponse, AnalysisSaved, AnalysisSummary

router = APIRouter(prefix="/api/v1", tags=["analyze"])


@router.post("/analyze", response_model=AnalysisSaved)
async def analyze(
    cv_file: UploadFile = File(...),
    job_description: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Full pipeline:
    1. Extract text from uploaded CV PDF
    2. Run RAG + Groq analysis
    3. Save result to PostgreSQL
    4. Return saved record (includes id and timestamps)
    """
    # Extract CV text
    cv_text = await extract_text_from_pdf(cv_file)

    # Run RAG analysis
    result: AnalysisResponse = await analyze_cv_match(cv_text, job_description)

    # Save to database — only analysis output, never the raw CV text
    record = Analysis(
        job_title=result.job_title,
        match_score=result.match_score,
        matching_skills=result.matching_skills,
        missing_skills=result.missing_skills,
        suggestions=result.suggestions,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return record


@router.get("/analyses", response_model=list[AnalysisSummary])
async def list_analyses(db: AsyncSession = Depends(get_db)):
    """
    This returns all non-expired analyses, most recent first.
    Filters out records past their expires_at date — soft expiry
    without needing a background cleanup job for now.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Analysis)
        .where(Analysis.expires_at > now)
        .order_by(Analysis.created_at.desc())
    )
    return result.scalars().all()


@router.get("/analyses/{analysis_id}", response_model=AnalysisSaved)
async def get_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns a single analysis by ID — full detail including skills and suggestions.
    Useful for the frontend to show a past result in full.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .where(Analysis.expires_at > now)
    )
    record = result.scalar_one_or_none()
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Analysis not found or expired.")
    return record