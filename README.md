# RAG Codebase Assistant

> Chat with any GitHub repository or local codebase using production-grade RAG (Retrieval-Augmented Generation)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

RAG Codebase Assistant is a powerful tool that lets you have intelligent conversations with any codebase. Ask questions like "How does authentication work?" or "What would break if I change this function?" and get accurate answers with code citations.

### Key Features

- **🎯 Code-Aware Chunking**: Uses tree-sitter to split code by function/class boundaries (not arbitrary character limits)
- **🔍 Hybrid Search**: Combines BM25 keyword search with vector similarity using Reciprocal Rank Fusion
- **📊 Dependency Analysis**: Tracks imports to understand code relationships and impact
- **💬 Smart Context**: Includes relevant imports and related files in responses
- **🌐 15+ Languages**: Python, JavaScript/TypeScript, Java, Go, Rust, C/C++, Ruby, and more
- **⚡ Multiple Interfaces**: CLI for quick queries, REST API for integration
- **💾 Local Storage**: ChromaDB vector database with no cloud dependency
- **🔄 Conversation History**: Natural follow-up questions with context

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/rag-codebase-assistant.git
cd rag-codebase-assistant

# Install dependencies
pip install -r requirements.txt

# Install the application so the `rag-code` terminal command works globally
pip install -e .

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Basic Usage

This tool comes with a built-in Command Line Interface (CLI) specifically designed for terminal use. 

```bash
# Index a GitHub repository
rag-code index https://github.com/pallets/flask

# Index a local directory
rag-code index ./my-project

# Start interactive chat
rag-code chat

# Ask a single question
rag-code ask "How does routing work?"
```

### Example Session

```
$ rag-code chat

You: How does user authentication work in this codebase?

Assistant: The authentication system uses JWT tokens with middleware:

1. Login Flow (auth/login.py):
   - Validates credentials against database
   - Generates JWT token with user ID
   - Returns token to client

2. Middleware (middleware/auth.py):
   - Validates JWT token on each request
   - Extracts user info and attaches to context
   - Returns 401 if invalid

3. Protected Routes (routes/api.py):
   - Use @require_auth decorator
   - Access user via request.user

You: What would break if I change the User.email field?

Assistant: Making User.email optional would impact:

**Direct Dependencies**:
- auth/login.py - Uses email for validation
- services/email_service.py - Sends emails
- api/users.py - Returns email in profiles

**Risk Level**: HIGH - Core authentication depends on email
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│  GitHub/Local → Code Scanner → Tree-sitter Chunker          │
│                      ↓                                       │
│              Dependency Graph Builder                        │
│                      ↓                                       │
│         OpenAI Embeddings → ChromaDB Storage                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    RETRIEVAL ENGINE                          │
├─────────────────────────────────────────────────────────────┤
│  Query → Hybrid Search (BM25 + Vector)                      │
│              ↓                                               │
│         Re-ranking (Cross-Encoder)                           │
│              ↓                                               │
│    Context Assembly (Code + Imports + Dependencies)         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      CHAT INTERFACE                          │
├─────────────────────────────────────────────────────────────┤
│  CLI / API → GPT-4 → Formatted Response                     │
└─────────────────────────────────────────────────────────────┘
```

## Advanced Features

### Configuration

Create a `config.json` file for custom settings:

```json
{
  "embedding_model": "text-embedding-3-small",
  "chat_model": "gpt-4-turbo-preview",
  "search_top_k": 20,
  "rerank_top_k": 5,
  "hybrid_search_alpha": 0.5,
  "max_context_tokens": 8000,
  "enable_cache": true
}
```

Or use environment variables:

```bash
export EMBEDDING_MODEL="text-embedding-3-small"
export CHAT_MODEL="gpt-4-turbo-preview"
export SEARCH_TOP_K=20
```

### Extended CLI Commands

```bash
# Show database statistics
rag-code stats

# Analyze impact of changing a file
rag-code impact src/auth.py

# Search without chat interface
rag-code search "authentication" --limit 10

# Cache management
rag-code cache-info
rag-code cache-clear
```

### REST API

Start the FastAPI server:

```bash
python -m src.api
# Server runs on http://localhost:8000
```

Index a repository:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"source": "https://github.com/user/repo"}'
```

Chat with the codebase:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How does authentication work?"}'
```

## How It Works

### 1. Code-Aware Chunking

Uses tree-sitter to parse code and split by semantic boundaries:

- Preserves complete function/class definitions
- Includes import statements as context
- Maintains code structure and readability
- Supports 15+ programming languages

### 2. Hybrid Search

Combines BM25 keyword search with vector similarity:

```
score = α × (1 / (k + vector_rank)) + (1-α) × (1 / (k + bm25_rank))
```

- Better than pure vector search for exact matches
- Better than pure keyword search for semantic queries
- Configurable α parameter (default 0.5)

### 3. Dependency Graph

Tracks import/require statements to build relationships:

- Find what files depend on a given file
- Transitive dependency analysis
- Impact assessment for code changes

### 4. Query Type Detection

Automatically adapts responses based on query intent:

| Query Type | Example | Behavior |
|------------|---------|----------|
| Explanation | "How does X work?" | Detailed code walkthrough |
| Impact Analysis | "What breaks if..." | Dependency graph analysis |
| Usage Search | "Find all usages" | Code search + examples |
| Test Generation | "Generate tests" | Test case creation |

## Supported Languages

Python, JavaScript, TypeScript, Java, Go, Rust, C, C++, Ruby, PHP, C#, Swift, Kotlin, Scala, Shell

## Performance

Tested on a medium-sized repository (Flask, ~50k LOC):

| Metric | Value |
|--------|-------|
| Indexing Speed | ~500 files/minute |
| Query Latency | 2-3 seconds |
| Embedding Cost | ~$0.10 per 100k LOC |
| Storage | ~50MB per 100k LOC |

## Project Structure

```
rag-codebase-assistant/
├── src/
│   ├── ingestion/          # Code loading and chunking
│   │   ├── cloner.py       # GitHub/local loader
│   │   ├── chunker.py      # Tree-sitter chunking
│   │   ├── embedder.py     # OpenAI embeddings
│   │   └── graph.py        # Dependency graph
│   ├── retrieval/          # Search and context
│   │   ├── hybrid_search.py # BM25 + vector
│   │   ├── reranker.py     # Cross-encoder
│   │   └── context_builder.py # Context assembly
│   ├── chat/               # LLM interaction
│   │   ├── engine.py       # Chat with history
│   │   └── prompts.py      # System prompts
│   ├── database.py         # ChromaDB interface
│   ├── config.py           # Configuration
│   ├── cache.py            # Caching layer
│   ├── utils.py            # Utilities
│   ├── cli.py              # Main CLI
│   ├── cli_extended.py     # Extended commands
│   └── api.py              # FastAPI server
├── tests/                  # Unit tests
├── examples/               # Usage examples
├── scripts/                # Utility scripts
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific test
pytest tests/test_chunker.py
```

### Installation for Development

```bash
# Install in editable mode
pip install -e .

# Install dev dependencies
pip install pytest pytest-cov black flake8
```

## Comparison with Alternatives

| Feature | RAG Codebase Assistant | GitHub Copilot Chat | Sourcegraph |
|---------|------------------------|---------------------|-------------|
| Works Offline | ✅ (after indexing) | ❌ | ❌ |
| Custom Codebases | ✅ Any repo | ✅ Open repos | ✅ |
| Dependency Analysis | ✅ Built-in | ⚠️ Limited | ✅ |
| Cost | Pay-per-use (OpenAI) | Subscription | Enterprise |
| Privacy | ✅ Local storage | ❌ Cloud-based | ❌ Cloud |
| Open Source | ✅ Apache 2.0 | ❌ Closed | Partial |
| Customizable | ✅ Fully | ❌ No | Limited |

## Troubleshooting

### "No indexed codebase found"
```bash
# Make sure you've indexed first
rag-code index ./your-project
```

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="sk-your-key"
```

### Slow indexing
- Large repos take time (normal)
- Check network speed for GitHub clones
- Consider indexing specific directories

### Tree-sitter parse errors
- Some files may fail to parse (normal)
- Check file encoding (should be UTF-8)
- Unsupported languages fall back to simple chunking

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tree-sitter](https://tree-sitter.github.io/) for code parsing
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [OpenAI](https://openai.com/) for embeddings and chat
- [Sentence Transformers](https://www.sbert.net/) for re-ranking

## Support

- **Issues**: [GitHub Issues](https://github.com/sairam3824/rag-codebase-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sairam3824/rag-codebase-assistant/discussions)

---

