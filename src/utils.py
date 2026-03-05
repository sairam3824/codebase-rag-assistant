"""Utility functions for RAG Codebase Assistant."""
import os
from pathlib import Path
from typing import Optional


def validate_openai_key() -> bool:
    """Check if OpenAI API key is set."""
    return bool(os.getenv("OPENAI_API_KEY"))


def get_project_root(file_path: Path) -> Path:
    """
    Find project root by looking for common markers.
    
    Args:
        file_path: Any file in the project
    
    Returns:
        Project root directory
    """
    current = file_path if file_path.is_dir() else file_path.parent
    
    # Look for common project markers
    markers = ['.git', 'setup.py', 'pyproject.toml', 'package.json', 'go.mod', 'Cargo.toml']
    
    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent
    
    # If no marker found, return original directory
    return file_path if file_path.is_dir() else file_path.parent


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count.
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to max length with ellipsis.
    
    Args:
        text: Input text
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
