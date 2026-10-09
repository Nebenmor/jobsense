# File: app/services/groq_service.py
import json
import logging
import re
from groq import AsyncGroq, APIError
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.analysis import AnalysisResponse
from app.services.retrieval_service import retrieve_relevant_snippets

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=settings.groq_api_key)


def _build_prompt(cv_text: str, job_description: str, snippets: list[str]) -> str:
    """
    Constructs the full RAG-augmented prompt sent to Groq.

    Structure:
    1. Role instruction
    2. Retrieved career-advice snippets (the "augmentation" in RAG)
    3. CV content
    4. Job description
    5. Output format instruction

    The snippets are injected between the role instruction and the CV/JD
    so the model reads the relevant advice before analyzing the match.
    This grounds the suggestions in specific retrieved reference material
    rather than relying purely on the model's general training knowledge.
    """
    # Format snippets as a numbered list for clarity in the prompt
    formatted_snippets = "\n".join(
        f"{i+1}. {snippet}" for i, snippet in enumerate(snippets)
    )

    return f"""You are a career advisor analyzing CV-to-job fit.

Use the following career advice principles when forming your suggestions.
These have been selected as specifically relevant to this job description:

{formatted_snippets}

---

CV Content:
{cv_text}

---

Job Description:
{job_description}

---

Analyze the match and respond ONLY in this JSON format, with no preamble,
no markdown code fences, and no extra commentary:
{{
  "job_title": "<short job title extracted from the job description>",
  "match_score": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "suggestions": ["specific actionable suggestion 1", "specific actionable suggestion 2"]
}}

Your suggestions must be grounded in the career advice principles above.
Be specific and honest. Do not give generic advice.
"""


def _parse_response(raw_text: str) -> dict:
    """
    Strip markdown fences defensively before parsing.
    The model occasionally wraps output in ```json blocks even when told not to.
    """
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


async def analyze_cv_match(cv_text: str, job_description: str) -> AnalysisResponse:
    """
    Full RAG pipeline:
    1. Retrieve — get top 4 relevant career-advice snippets for this JD
    2. Augment  — inject snippets into the prompt alongside CV + JD
    3. Generate — call Groq, parse and validate structured JSON response

    Retries once if the response isn't valid JSON.
    Returns a clean 502 if the Groq API itself fails (bad model, rate limit, outage).
    """
    # ── Step 1: Retrieve ─────────────────────────────────────────────────────
    # Score the job description against the career-advice snippets and fetch
    # the 4 most relevant. This is the "R" in RAG — retrieval happens before
    # the LLM call.
    snippets = retrieve_relevant_snippets(job_description, top_k=4)

    # ── Step 2: Augment ──────────────────────────────────────────────────────
    # Build the prompt with retrieved snippets injected.
    # This is the "A" in RAG — the prompt is augmented with retrieved context.
    prompt = _build_prompt(cv_text, job_description, snippets)

    # ── Step 3: Generate ─────────────────────────────────────────────────────
    # Call the LLM with the augmented prompt and parse the response.
    # This is the "G" in RAG — generation grounded in retrieved material.
    for attempt in range(2):
        try:
            response = await client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
        except APIError as e:
            # Handled here so the client gets a proper JSON error (with CORS
            # headers) instead of an unhandled 500 that the browser reports
            # as a CORS failure.
            logger.error("Groq API error: %s", e)
            raise HTTPException(
                status_code=502,
                detail="The AI service is currently unavailable. Please try again later."
            ) from e

        raw_text = response.choices[0].message.content or ""

        try:
            parsed = _parse_response(raw_text)
            return AnalysisResponse(**parsed)
        except (json.JSONDecodeError, ValueError):
            if attempt == 1:
                raise HTTPException(
                    status_code=502,
                    detail="Failed to get a valid analysis from the AI service. Please try again."
                )
            continue