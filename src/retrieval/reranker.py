"""Re-rank search results for better relevance."""
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder


class Reranker:
    """Re-rank search results using cross-encoder."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results using cross-encoder.
        
        Args:
            query: Search query
            results: Initial search results
            top_k: Number of results to return
        
        Returns:
            Re-ranked results
        """
        if not results:
            return []
        
        # Prepare pairs for cross-encoder
        pairs = [[query, result['content']] for result in results]
        
        # Get cross-encoder scores
        scores = self.model.predict(pairs)
        
        # Add rerank scores and sort
        for i, result in enumerate(results):
            result['rerank_score'] = float(scores[i])
        
        results.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return results[:top_k]
