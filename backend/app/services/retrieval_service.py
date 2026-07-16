# File: app/services/retrieval_service.py
import json
from pathlib import Path

_data_dir = Path(__file__).parent.parent / "data"

with open(_data_dir / "career_snippets.json", "r") as f:
    _snippets: list[dict] = json.load(f)

_snippet_texts: list[str] = [s["text"] for s in _snippets]


def retrieve_relevant_snippets(job_description: str, top_k: int = 4) -> list[str]:
    """
    Returns the top_k most relevant career-advice snippets for a given
    job description using keyword-based scoring.

    This replaces the sentence-transformers cosine similarity approach
    to avoid loading a 400MB model on the server — which exceeds
    Render's free tier 512MB RAM limit.

    The keyword approach works well for this use case because job descriptions
    contain specific, distinctive terms (e.g. 'AWS', 'backend', 'leadership')
    that map directly to the categories in our snippet knowledge base.
    """
    jd_lower = job_description.lower()
    scored = []

    for idx, snippet in enumerate(_snippets):
        score = 0
        snippet_lower = snippet["text"].lower()

        # Score based on category keyword match
        category = snippet.get("category", "")
        category_keywords = {
            "backend": ["backend", "api", "server", "fastapi", "django", "flask", "node", "python"],
            "frontend": ["frontend", "react", "vue", "angular", "ui", "css", "html", "javascript"],
            "fullstack": ["full stack", "fullstack", "full-stack", "end-to-end"],
            "cloud": ["aws", "azure", "gcp", "cloud", "kubernetes", "docker", "devops"],
            "leadership": ["lead", "manager", "management", "team lead", "director", "head of"],
            "data": ["data", "analytics", "sql", "database", "pipeline", "etl", "spark"],
            "mobile": ["mobile", "ios", "android", "react native", "flutter", "swift", "kotlin"],
            "security": ["security", "penetration", "vulnerability", "compliance", "soc2", "owasp"],
            "testing": ["test", "qa", "quality", "jest", "pytest", "cypress", "automation"],
            "quantification": ["metrics", "impact", "results", "achievements", "performance"],
            "keywords": ["ats", "keywords", "applicant tracking", "resume", "cv"],
            "startups": ["startup", "scale", "growth", "founding", "early stage"],
            "enterprise": ["enterprise", "corporate", "large company", "fortune", "cross-team"],
            "devops": ["devops", "ci/cd", "pipeline", "deployment", "infrastructure", "terraform"],
        }

        if category in category_keywords:
            for kw in category_keywords[category]:
                if kw in jd_lower:
                    score += 3  # strong signal — category directly matches JD

        # Additional score for word overlap between snippet and JD
        snippet_words = set(snippet_lower.split())
        jd_words = set(jd_lower.split())
        overlap = len(snippet_words & jd_words)
        score += overlap

        scored.append((idx, score))

    top_results = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]
    return [_snippet_texts[idx] for idx, _ in top_results]