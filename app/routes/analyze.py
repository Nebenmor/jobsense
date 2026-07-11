# File: app/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, Form

from app.services.pdf_service import extract_text_from_pdf
from app.services.groq_service import analyze_cv_match
from app.schemas.analysis import AnalysisResponse

router = APIRouter(prefix="/api/v1", tags=["analyze"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    cv_file: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Day 1 version: no database save yet — just returns the analysis directly
    so we can test the core pipeline (PDF -> Groq/Llama -> structured JSON) in isolation.
    """
    cv_text = await extract_text_from_pdf(cv_file)
    result = await analyze_cv_match(cv_text, job_description)
    return result