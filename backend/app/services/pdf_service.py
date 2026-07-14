# File: app/services/pdf_service.py
import pdfplumber
import io
from fastapi import HTTPException, UploadFile

from app.core.config import settings


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Reads an uploaded PDF file and returns its plain text content.
    Raises HTTPException for invalid files so the route layer
    can return a clean error to the frontend.
    """
    # --- Validation 1: file type ---
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_bytes = await file.read()

    # --- Validation 2: file size ---
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_cv_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {settings.max_cv_size_mb}MB."
        )

    # --- Extraction ---
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    # --- Validation 3: did we actually get text? ---
    if len(full_text) < 50:
        raise HTTPException(
            status_code=422,
            detail=(
                "Couldn't read text from this PDF. "
                "It may be a scanned image — please upload a text-based PDF."
            )
        )

    return full_text