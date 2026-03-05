"""Setup script for RAG Codebase Assistant."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rag-codebase-assistant",
    version="0.1.0",
    author="RAG Codebase Assistant Contributors",
    description="Chat with any GitHub repository using RAG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rag-codebase-assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.12.0",
        "chromadb>=0.4.22",
        "tree-sitter>=0.20.4",
        "rank-bm25>=0.2.2",
        "gitpython>=3.1.41",
        "click>=8.1.7",
        "rich>=13.7.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "sentence-transformers>=2.3.1",
        "numpy>=1.24.0",
        "tiktoken>=0.5.2",
    ],
    entry_points={
        "console_scripts": [
            "rag-code=src.cli:cli",
        ],
    },
)
