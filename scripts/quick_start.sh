#!/bin/bash
# Quick start script for RAG Codebase Assistant

set -e

echo "🚀 RAG Codebase Assistant - Quick Start"
echo "========================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "   Please set it: export OPENAI_API_KEY='your-key'"
    exit 1
fi

echo "✓ OpenAI API key found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo "✓ Dependencies installed"

# Run a test
echo ""
echo "🧪 Running tests..."
pytest tests/ -q

echo ""
echo "✅ Setup complete!"
echo ""
echo "Try these commands:"
echo "  rag-code index https://github.com/pallets/flask"
echo "  rag-code chat"
echo "  rag-code ask 'How does routing work?'"
