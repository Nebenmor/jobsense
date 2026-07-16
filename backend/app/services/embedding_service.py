# File: app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np

# Lazy loading — model loads only on first call, not at import time.
# This avoids loading the model during startup health checks,
# and means cold starts are faster even if the model is needed.
_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> np.ndarray:
    """
    Embeds a single string into a vector.
    Used at query time to embed the incoming job description.
    """
    return _get_model().encode(text, convert_to_numpy=True)


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Embeds a list of strings in one batch.
    Used locally to pre-compute snippet embeddings — not called on the server.
    """
    return _get_model().encode(texts, convert_to_numpy=True)