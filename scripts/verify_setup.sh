#!/bin/bash
# Verify project setup

echo "🔍 Verifying RAG Codebase Assistant Setup"
echo "=========================================="

# Check Python version
echo -n "Python version: "
python3 --version

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "✓ requirements.txt found"
else
    echo "✗ requirements.txt not found"
    exit 1
fi

# Check project structure
echo ""
echo "Checking project structure..."
dirs=("src" "tests" "examples" "docs" "scripts")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ exists"
    else
        echo "✗ $dir/ missing"
    fi
done

# Check key files
echo ""
echo "Checking key files..."
files=(
    "src/cli.py"
    "src/database.py"
    "src/api.py"
    "README.md"
    "LICENSE"
    "setup.py"
)
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

# Check Python syntax
echo ""
echo "Checking Python syntax..."
python3 -m py_compile src/cli.py 2>/dev/null && echo "✓ src/cli.py syntax OK" || echo "✗ src/cli.py has errors"
python3 -m py_compile src/database.py 2>/dev/null && echo "✓ src/database.py syntax OK" || echo "✗ src/database.py has errors"
python3 -m py_compile src/api.py 2>/dev/null && echo "✓ src/api.py syntax OK" || echo "✗ src/api.py has errors"

echo ""
echo "=========================================="
echo "Setup verification complete!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Set API key: export OPENAI_API_KEY='your-key'"
echo "3. Index a repo: rag-code index https://github.com/user/repo"
echo "4. Start chatting: rag-code chat"
