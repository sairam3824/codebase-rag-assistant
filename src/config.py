"""Configuration management for RAG Codebase Assistant."""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import json


@dataclass
class Config:
    """Application configuration."""
    
    # OpenAI settings
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4-turbo-preview"
    
    # Database settings
    chroma_db_path: str = "./chroma_db"
    
    # Search settings
    search_top_k: int = 20
    rerank_top_k: int = 5
    hybrid_search_alpha: float = 0.5  # Weight for vector search
    
    # Context settings
    max_context_tokens: int = 8000
    
    # Cache settings
    enable_cache: bool = True
    cache_dir: str = "./.cache"
    cache_ttl_hours: int = 24
    
    # Chunking settings
    max_chunk_size: int = 2000
    chunk_overlap: int = 200
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        return cls(
            openai_api_key=api_key,
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            chat_model=os.getenv("CHAT_MODEL", "gpt-4-turbo-preview"),
            chroma_db_path=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
            search_top_k=int(os.getenv("SEARCH_TOP_K", "20")),
            rerank_top_k=int(os.getenv("RERANK_TOP_K", "5")),
            hybrid_search_alpha=float(os.getenv("HYBRID_SEARCH_ALPHA", "0.5")),
            max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "8000")),
            enable_cache=os.getenv("ENABLE_CACHE", "true").lower() == "true",
            cache_dir=os.getenv("CACHE_DIR", "./.cache"),
            cache_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        # Merge with environment variables (env takes precedence)
        api_key = os.getenv("OPENAI_API_KEY") or data.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not found in config or environment")
        
        return cls(
            openai_api_key=api_key,
            embedding_model=os.getenv("EMBEDDING_MODEL") or data.get("embedding_model", "text-embedding-3-small"),
            chat_model=os.getenv("CHAT_MODEL") or data.get("chat_model", "gpt-4-turbo-preview"),
            chroma_db_path=data.get("chroma_db_path", "./chroma_db"),
            search_top_k=data.get("search_top_k", 20),
            rerank_top_k=data.get("rerank_top_k", 5),
            hybrid_search_alpha=data.get("hybrid_search_alpha", 0.5),
            max_context_tokens=data.get("max_context_tokens", 8000),
            enable_cache=data.get("enable_cache", True),
            cache_dir=data.get("cache_dir", "./.cache"),
            cache_ttl_hours=data.get("cache_ttl_hours", 24),
        )
    
    def save(self, config_path: Path):
        """Save configuration to JSON file."""
        data = {
            "embedding_model": self.embedding_model,
            "chat_model": self.chat_model,
            "chroma_db_path": self.chroma_db_path,
            "search_top_k": self.search_top_k,
            "rerank_top_k": self.rerank_top_k,
            "hybrid_search_alpha": self.hybrid_search_alpha,
            "max_context_tokens": self.max_context_tokens,
            "enable_cache": self.enable_cache,
            "cache_dir": self.cache_dir,
            "cache_ttl_hours": self.cache_ttl_hours,
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config):
    """Set global configuration instance."""
    global _config
    _config = config
