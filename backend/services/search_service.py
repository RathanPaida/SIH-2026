"""Hybrid search service using FAISS (semantic) + BM25 (keyword) scoring.

Loads standards from the database, builds:
1. FAISS index from sentence embeddings of title + scope
2. BM25 index from tokenized title + scope + keywords

hybrid_search() combines both scores with configurable weights.
"""

import json
import numpy as np
from typing import Optional

from config import EMBEDDING_MODEL, FAISS_WEIGHT, BM25_WEIGHT, TOP_K_RESULTS

# Lazy-loaded globals
_faiss_index = None
_bm25_index = None
_standards_list = []  # List of dicts with id, is_number, title, scope, keywords
_embedder = None


def _get_embedder():
    """Lazy-load the sentence-transformer model."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def _build_standard_text(std: dict) -> str:
    """Combine standard fields into a single searchable text."""
    parts = [std.get("is_number", ""), std.get("title", "")]
    if std.get("scope"):
        parts.append(std["scope"])
    if std.get("keywords"):
        kw = std["keywords"]
        if isinstance(kw, str):
            try:
                kw = json.loads(kw)
            except json.JSONDecodeError:
                kw = [kw]
        parts.extend(kw)
    return " ".join(parts)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenization."""
    import re
    tokens = re.findall(r'\b\w+\b', text.lower())
    # Remove very short tokens and common stop words
    stop_words = {"the", "of", "and", "for", "in", "to", "a", "is", "with", "as", "by", "on", "at", "an", "or", "be"}
    return [t for t in tokens if len(t) > 1 and t not in stop_words]


def build_index(standards: list[dict]):
    """Build both FAISS and BM25 indexes from a list of standard dicts."""
    global _faiss_index, _bm25_index, _standards_list

    _standards_list = standards

    if not standards:
        print("[Search] No standards to index.")
        return

    # Build text corpus
    texts = [_build_standard_text(s) for s in standards]

    # --- FAISS Index ---
    try:
        import faiss
        embedder = _get_embedder()
        embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        embeddings = embeddings.astype(np.float32)

        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        embeddings = embeddings / norms

        dim = embeddings.shape[1]
        _faiss_index = faiss.IndexFlatIP(dim)  # Inner product = cosine sim for normalized vectors
        _faiss_index.add(embeddings)
        print(f"[Search] FAISS index built with {len(standards)} vectors (dim={dim})")
    except Exception as e:
        print(f"[Search] FAISS index build failed: {e}. Falling back to numpy.")
        # Fallback: store embeddings in numpy array
        embedder = _get_embedder()
        embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        _faiss_index = embeddings / norms  # Store as numpy array for manual cosine sim

    # --- BM25 Index ---
    try:
        from rank_bm25 import BM25Okapi
        tokenized_corpus = [_tokenize(t) for t in texts]
        _bm25_index = BM25Okapi(tokenized_corpus)
        print(f"[Search] BM25 index built with {len(standards)} documents")
    except Exception as e:
        print(f"[Search] BM25 index build failed: {e}")
        _bm25_index = None


def hybrid_search(query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
    """
    Search for standards matching the query using hybrid FAISS + BM25 scoring.

    Returns list of dicts: {standard_id, is_number, title, scope, score}
    """
    if not _standards_list:
        return []

    n = len(_standards_list)
    faiss_scores = np.zeros(n)
    bm25_scores = np.zeros(n)

    # --- FAISS / Semantic Search ---
    if _faiss_index is not None:
        import faiss as faiss_lib
        embedder = _get_embedder()
        query_emb = embedder.encode([query], convert_to_numpy=True).astype(np.float32)
        query_norm = np.linalg.norm(query_emb, axis=1, keepdims=True)
        if query_norm[0][0] > 0:
            query_emb = query_emb / query_norm

        if isinstance(_faiss_index, np.ndarray):
            # Numpy fallback
            sims = np.dot(_faiss_index, query_emb.T).flatten()
            faiss_scores = np.clip(sims, 0, 1)
        else:
            # FAISS index
            distances, indices = _faiss_index.search(query_emb, min(top_k * 3, n))
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < n:
                    faiss_scores[idx] = max(0, dist)  # IP score

    # --- BM25 / Keyword Search ---
    if _bm25_index is not None:
        query_tokens = _tokenize(query)
        if query_tokens:
            scores = _bm25_index.get_scores(query_tokens)
            # Normalize BM25 scores to [0, 1]
            max_score = max(scores) if max(scores) > 0 else 1
            bm25_scores = scores / max_score

    # --- Hybrid Score ---
    hybrid_scores = FAISS_WEIGHT * faiss_scores + BM25_WEIGHT * bm25_scores

    # Get top-k indices
    top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        score = float(hybrid_scores[idx])
        if score < 0.01:  # Skip very low scores
            continue
        std = _standards_list[idx]
        results.append({
            "standard_id": std["id"],
            "is_number": std["is_number"],
            "title": std["title"],
            "scope": std.get("scope", ""),
            "keywords": std.get("keywords", ""),
            "sector": std.get("sector", ""),
            "score": round(score, 4),
        })

    return results


def is_index_ready() -> bool:
    """Check if search indexes are built."""
    return len(_standards_list) > 0
