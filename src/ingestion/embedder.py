"""Generate embeddings using OpenAI API."""
from typing import List, Optional
from openai import OpenAI
import os
import time


class Embedder:
    """Generate embeddings for code chunks."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def embed_texts(self, texts: List[str], max_retries: int = 3) -> List[List[float]]:
        """Generate embeddings for a list of texts with retry logic."""
        if not texts:
            return []
        
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Embedding attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to generate embeddings after {max_retries} attempts: {e}")
    
    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.embed_texts([text])[0]
