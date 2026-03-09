# RAG Codebase Assistant

> Chat with any GitHub repository or local codebase using Retrieval-Augmented Generation (RAG).

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## What This Project Does

RAG Codebase Assistant indexes source code, retrieves relevant code chunks, and answers questions using LLMs with code context.

You can ask:
- "How does authentication work?"
- "Where is this function used?"
- "What could break if I change this file?"

## Quick Start (5 commands)

```bash
cd rag-codebase-assistant
pip install -r requirements.txt
pip install -e .
export OPENAI_API_KEY="sk-your-api-key-here"
rag-code index ./my-project && rag-code chat
```

## Features

- Code-aware chunking via tree-sitter (functions/classes instead of fixed character windows)
- Vector retrieval in ChromaDB
- Cross-encoder reranking for better relevance
- Import-based dependency graph for impact analysis
- CLI for interactive chat and one-shot questions
- FastAPI server for programmatic usage
- Persistent local storage (`./chroma_db` by default)

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

```bash
git clone https://github.com/yourusername/rag-codebase-assistant.git
cd rag-codebase-assistant

pip install -r requirements.txt
pip install -e .

export OPENAI_API_KEY="sk-your-api-key-here"
```

Verify installation:

```bash
rag-code --help
```

## CLI Usage

### Core workflow

```bash
# 1) Index a local repository
rag-code index ./my-project

# 2) Start interactive chat
rag-code chat

# 3) Or ask one question directly
rag-code ask "How does routing work?"
```

### Full command set

```bash
rag-code index <source>
rag-code chat
rag-code ask "<question>"
rag-code stats
rag-code impact <file_path>
rag-code search "<query>" --limit 10
rag-code cache-info
rag-code cache-clear
```

Examples:

```bash
# Index GitHub repository
rag-code index https://github.com/pallets/flask

# Search without chat
rag-code search "authentication" --limit 10

# Impact analysis
rag-code impact src/auth.py
```

## REST API

Start the API server:

```bash
python -m src.api
# runs on http://localhost:8000
```

### Endpoints

- `POST /index`
- `POST /chat`
- `GET /stats`
- `POST /clear`

### Example requests

Index GitHub repo:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"source": "https://github.com/user/repo"}'
```

Index local directory:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"source": "./my-project"}'
```

Chat:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How does authentication work?"}'
```

## How It Works

1. Ingestion
- Loads source from local path or GitHub.
- Scans supported code files.
- Uses tree-sitter to chunk code by semantic boundaries.
- Extracts imports for dependency tracking.

2. Indexing
- Generates embeddings using OpenAI embeddings API.
- Stores documents + metadata in ChromaDB.
- Persists dependency graph to `<db_path>/dependency_graph.json`.

3. Retrieval and answer generation
- Retrieves candidates with vector search from ChromaDB.
- Re-ranks candidates with a sentence-transformers cross-encoder.
- Builds token-limited context.
- Sends context + query to chat model for final response.

Note: `src/retrieval/hybrid_search.py` includes BM25+vector RRF utility logic, while the default runtime path uses vector retrieval + reranking.

## Configuration

Environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export EMBEDDING_MODEL="text-embedding-3-small"
export CHAT_MODEL="gpt-4-turbo-preview"
export SEARCH_TOP_K=20
```

You can also use `config.example.json` as a template for custom integrations.

## Supported Languages

Python, JavaScript, TypeScript, Java, Go, Rust, C, C++, Ruby, PHP, C#, Swift, Kotlin, Scala, Shell

## Project Structure

```text
rag-codebase-assistant/
├── src/
│   ├── ingestion/
│   │   ├── cloner.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── graph.py
│   ├── retrieval/
│   │   ├── hybrid_search.py
│   │   ├── reranker.py
│   │   └── context_builder.py
│   ├── chat/
│   │   ├── engine.py
│   │   └── prompts.py
│   ├── cli.py
│   ├── cli_extended.py
│   ├── api.py
│   ├── database.py
│   ├── config.py
│   └── cache.py
├── tests/
├── examples/
├── scripts/
├── requirements.txt
├── setup.py
└── torun.txt
```

## Troubleshooting

### `rag-code: command not found`

```bash
pip install -e .
```

### `ModuleNotFoundError` for parser/search libraries

```bash
pip install -r requirements.txt
```

### `OpenAI API key not found`

```bash
export OPENAI_API_KEY="sk-your-key"
```

### `No indexed codebase found`

```bash
rag-code index ./your-project
```

### Impact analysis shows no results after upgrade

Re-index once so dependency graph persistence file is generated in the DB directory.

## Development

Run tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## License

MIT License. See [LICENSE](LICENSE).
