# File: app/services/groq_service.py
import json
import re
from groq import Groq
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.analysis import AnalysisResponse

client = Groq(api_key=settings.groq_api_key)


def _build_prompt(cv_text: str, job_description: str) -> str:
    """
    Constructs the prompt sent to Groq/Llama.
    Note: in Day 3, retrieved RAG snippets will be injected here too.
    """
    return f"""You are a career advisor analyzing CV-to-job fit.

CV Content:
{cv_text}

Job Description:
{job_description}

Analyze the match and respond ONLY in this JSON format, with no preamble, \
no markdown code fences, and no extra commentary:
{{
  "job_title": "<short job title extracted from the job description>",
  "match_score": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "suggestions": ["specific actionable suggestion 1", "specific actionable suggestion 2"]
}}

Be specific and honest. Suggestions should be concrete, not generic advice.
"""


def _parse_response(raw_text: str) -> dict:
    """
    Strip markdown fences defensively before parsing.
    """
    cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


async def analyze_cv_match(cv_text: str, job_description: str) -> AnalysisResponse:
    """
    Sends CV + job description to Groq (Llama 3.3 70B) and returns a
    validated, structured analysis. Retries once if response isn't valid JSON.
    """
    prompt = _build_prompt(cv_text, job_description)

    for attempt in range(2):
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # lower = more consistent, structured output
        )
        raw_text = response.choices[0].message.content

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