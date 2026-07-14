# File: app/services/retrieval_service.py
import json
import numpy as np
from pathlib import Path

from app.services.embedding_service import embed_text, embed_texts

# ── Load and pre-embed snippets once at startup ────────────────────────────
# Reading from disk and running the embedding model takes ~1 second.
# We do this once when the module loads and keep everything in memory.
# This means every incoming request gets instant retrieval — no re-embedding.

_snippets_path = Path(__file__).parent.parent / "data" / "career_snippets.json"

with open(_snippets_path, "r") as f:
    _snippets: list[dict] = json.load(f)

_snippet_texts: list[str] = [s["text"] for s in _snippets]

# This is the "vector index" — a 2D array where each row is the
# embedded vector for the corresponding snippet text.
# Shape: (25, 384) — 25 snippets, each with a 384-dimensional vector.
_snippet_embeddings: np.ndarray = embed_texts(_snippet_texts)


# ── Cosine similarity ───────────────────────────────────────────────────────

def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Measures how similar two vectors are, regardless of their magnitude.
    Returns a value between -1 (opposite) and 1 (identical meaning).
    
    How it works:
    - If two texts mean the same thing, their vectors point in the same
      direction → dot product is high → cosine similarity is close to 1
    - If two texts mean different things, their vectors point in different
      directions → dot product is low → cosine similarity is close to 0
    """
    dot_product = np.dot(vec_a, vec_b)
    magnitude = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if magnitude == 0:
        return 0.0
    return float(dot_product / magnitude)


# ── Public retrieval function ───────────────────────────────────────────────

def retrieve_relevant_snippets(job_description: str, top_k: int = 4) -> list[str]:
    """
    Given a job description, returns the top_k most relevant
    career-advice snippets from our knowledge base.

    Steps:
    1. Embed the job description into a vector
    2. Compare that vector against all 25 pre-embedded snippet vectors
    3. Sort by similarity score (highest first)
    4. Return the text of the top_k snippets

    These snippets will be injected into the Groq prompt in Day 3,
    grounding the AI's suggestions in specific, retrieved reference material.
    """
    query_vector = embed_text(job_description)

    # Score every snippet against the query
    scored = [
        (idx, _cosine_similarity(query_vector, snippet_vec))
        for idx, snippet_vec in enumerate(_snippet_embeddings)
    ]

    # Sort by score descending, take top_k
    top_results = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]

    # Return the actual text of the top snippets
    return [_snippet_texts[idx] for idx, _ in top_results]