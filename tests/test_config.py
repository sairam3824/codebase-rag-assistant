"""Tests for configuration management."""
import pytest
import os
from pathlib import Path
from src.config import Config


def test_config_from_env(monkeypatch):
    """Test loading config from environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL", "custom-model")
    
    config = Config.from_env()
    
    assert config.openai_api_key == "test-key"
    assert config.embedding_model == "custom-model"
    assert config.chat_model == "gpt-4-turbo-preview"  # default


def test_config_missing_api_key():
    """Test error when API key is missing."""
    # Clear environment
    old_key = os.environ.pop("OPENAI_API_KEY", None)
    
    try:
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            Config.from_env()
    finally:
        # Restore
        if old_key:
            os.environ["OPENAI_API_KEY"] = old_key


def test_config_defaults():
    """Test default configuration values."""
    config = Config(openai_api_key="test-key")
    
    assert config.search_top_k == 20
    assert config.rerank_top_k == 5
    assert config.hybrid_search_alpha == 0.5
    assert config.enable_cache is True
