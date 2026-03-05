"""Hybrid search combining BM25 and vector similarity."""
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import numpy as np


class HybridSearcher:
    """Combine BM25 keyword search with vector similarity."""
    
    def __init__(self, alpha: float = 0.5):
        """
        Args:
            alpha: Weight for vector search (1-alpha for BM25)
        """
        self.alpha = alpha
        self.bm25 = None
        self.corpus = []
        self.metadata = []
    
    def index_documents(self, documents: List[str], metadata: List[Dict[str, Any]]):
        """Index documents for BM25 search."""
        self.corpus = documents
        self.metadata = metadata
        tokenized_corpus = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    def search(
        self,
        query: str,
        vector_scores: List[float],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using Reciprocal Rank Fusion.
        
        Args:
            query: Search query
            vector_scores: Similarity scores from vector search
            top_k: Number of results to return
        
        Returns:
            List of results with fused scores
        """
        # BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Normalize scores to [0, 1]
        bm25_scores = self._normalize_scores(bm25_scores)
        vector_scores = self._normalize_scores(np.array(vector_scores))
        
        # Reciprocal Rank Fusion
        bm25_ranks = self._scores_to_ranks(bm25_scores)
        vector_ranks = self._scores_to_ranks(vector_scores)
        
        k = 60  # RRF constant
        fused_scores = []
        
        for i in range(len(self.corpus)):
            rrf_score = (
                1 / (k + bm25_ranks[i]) * (1 - self.alpha) +
                1 / (k + vector_ranks[i]) * self.alpha
            )
            fused_scores.append(rrf_score)
        
        # Get top-k results
        top_indices = np.argsort(fused_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'content': self.corpus[idx],
                'metadata': self.metadata[idx],
                'score': fused_scores[idx],
                'bm25_score': bm25_scores[idx],
                'vector_score': vector_scores[idx]
            })
        
        return results
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to [0, 1] range."""
        if len(scores) == 0:
            return scores
        min_score = scores.min()
        max_score = scores.max()
        if max_score - min_score == 0:
            return np.ones_like(scores)
        return (scores - min_score) / (max_score - min_score)
    
    def _scores_to_ranks(self, scores: np.ndarray) -> np.ndarray:
        """Convert scores to ranks (0 = best)."""
        return len(scores) - np.argsort(np.argsort(scores)) - 1
