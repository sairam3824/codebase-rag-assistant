"""Tests for hybrid search."""
import pytest
from src.retrieval.hybrid_search import HybridSearcher


def test_hybrid_search():
    """Test hybrid search with BM25 and vector scores."""
    searcher = HybridSearcher(alpha=0.5)
    
    documents = [
        "def authenticate(user, password): return check_password(user, password)",
        "def login(username, pwd): return authenticate(username, pwd)",
        "def logout(session): session.clear()"
    ]
    
    metadata = [
        {"file": "auth.py", "name": "authenticate"},
        {"file": "auth.py", "name": "login"},
        {"file": "session.py", "name": "logout"}
    ]
    
    searcher.index_documents(documents, metadata)
    
    # Mock vector scores (would come from embeddings)
    vector_scores = [0.9, 0.7, 0.3]
    
    results = searcher.search("authentication", vector_scores, top_k=2)
    
    assert len(results) == 2
    assert results[0]['metadata']['name'] in ['authenticate', 'login']


def test_score_normalization():
    """Test score normalization."""
    searcher = HybridSearcher()
    
    import numpy as np
    scores = np.array([1.0, 5.0, 10.0])
    normalized = searcher._normalize_scores(scores)
    
    assert normalized.min() == 0.0
    assert normalized.max() == 1.0
