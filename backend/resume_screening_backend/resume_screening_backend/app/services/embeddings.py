"""
Generates transformer-based sentence embeddings using sentence-transformers.

The model is loaded lazily (on first use) and cached as a module-level
singleton so it is only loaded into memory once per process.
"""
import threading
from typing import List

import numpy as np

from app.config import settings

_model = None
_model_lock = threading.Lock()


def get_model():
    """Lazily load and cache the sentence-transformer model (thread-safe)."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:  # double-checked locking
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def generate_embedding(text: str) -> List[float]:
    """Generate a single embedding vector for a piece of text."""
    model = get_model()
    # Truncate very long documents to keep inference fast; the model itself
    # also has an internal max sequence length and will truncate further.
    truncated = text[:20000]
    vector = model.encode(truncated, normalize_embeddings=True)
    return vector.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple documents in a single batched call."""
    model = get_model()
    truncated = [t[:20000] for t in texts]
    vectors = model.encode(truncated, normalize_embeddings=True, batch_size=16)
    return np.asarray(vectors).tolist()
