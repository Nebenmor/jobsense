# File: app/services/embedding_service.py
# NOTE: This file is used locally only — not imported by the server.
# It was used to pre-compute snippet_embeddings.json.
# The server uses keyword-based retrieval (retrieval_service.py) instead,
# to avoid loading a 400MB model on Render's 512MB free tier.

def embed_text(text: str):
    raise NotImplementedError("embedding_service is local-only.")

def embed_texts(texts: list[str]):
    raise NotImplementedError("embedding_service is local-only.")