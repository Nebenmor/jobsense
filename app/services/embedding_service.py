# File: app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np

# Load the model once when the module is imported.
# "all-MiniLM-L6-v2" is small (80MB), fast, and accurate enough for this use case.
# It downloads automatically on first run and is cached locally after that.
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> np.ndarray:
    """
    Converts a string into a vector (1D numpy array of floats).
    The vector captures the semantic meaning of the text.

    Example: embed_text("Python backend developer") and
    embed_text("FastAPI REST API engineer") will produce vectors
    that are close together — similar meaning, different words.
    """
    return _model.encode(text, convert_to_numpy=True)


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Embeds a list of strings in one batch — more efficient than
    calling embed_text() in a loop. Returns a 2D array where
    each row is the vector for the corresponding text.
    """
    return _model.encode(texts, convert_to_numpy=True)