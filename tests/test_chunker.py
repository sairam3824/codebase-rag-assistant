"""Tests for code chunker."""
import pytest
from pathlib import Path
from src.ingestion.chunker import CodeChunker, CodeChunk


def test_python_chunking():
    """Test chunking Python code."""
    chunker = CodeChunker()
    
    code = '''
import os
from typing import List

def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"

class Greeter:
    def greet(self, name: str):
        return hello(name)
'''
    
    chunks = chunker.chunk_file(Path("test.py"), code)
    
    assert len(chunks) >= 2  # At least function and class
    assert any(c.name == "hello" for c in chunks)
    assert any(c.name == "Greeter" for c in chunks)
    assert all(c.language == "python" for c in chunks)


def test_unsupported_language():
    """Test fallback for unsupported languages."""
    chunker = CodeChunker()
    
    code = "SELECT * FROM users;"
    chunks = chunker.chunk_file(Path("query.sql"), code)
    
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "file"


def test_imports_extraction():
    """Test import statement extraction."""
    chunker = CodeChunker()
    
    code = '''
import os
from typing import List

def test():
    pass
'''
    
    chunks = chunker.chunk_file(Path("test.py"), code)
    
    # Check that imports are captured
    assert any(len(c.imports) > 0 for c in chunks)
