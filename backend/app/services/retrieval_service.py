# File: app/services/retrieval_service.py
import json
import numpy as np
from pathlib import Path

from app.services.embedding_service import embed_text

_data_dir = Path(__file__).parent.parent / "data"

# Load snippets
with open(_data_dir / "career_snippets.json", "r") as f:
    _snippets: list[dict] = json.load(f)

_snippet_texts: list[str] = [s["text"] for s in _snippets]

# Load pre-computed embeddings from file — no model needed at runtime
with open(_data_dir / "snippet_embeddings.json", "r") as f:
    _snippet_embeddings: np.ndarray = np.array(json.load(f))


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    dot_product = np.dot(vec_a, vec_b)
    magnitude = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if magnitude == 0:
        return 0.0
    return float(dot_product / magnitude)


def retrieve_relevant_snippets(job_description: str, top_k: int = 4) -> list[str]:
    """
    Embeds the job description query and retrieves top_k most relevant
    career-advice snippets using cosine similarity.

    Snippet embeddings are pre-computed and loaded from file —
    the embedding model is only used at query time (for the JD),
    not for the static knowledge base. This keeps memory usage low
    enough to run on Render's free tier.
    """
    query_vector = embed_text(job_description)

    scored = [
        (idx, _cosine_similarity(query_vector, snippet_vec))
        for idx, snippet_vec in enumerate(_snippet_embeddings)
    ]

    top_results = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]
    return [_snippet_texts[idx] for idx, _ in top_results]