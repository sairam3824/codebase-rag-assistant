.PHONY: install test clean run-api help

help:
	@echo "RAG Codebase Assistant - Available Commands"
	@echo "==========================================="
	@echo "make install    - Install dependencies"
	@echo "make test       - Run tests"
	@echo "make clean      - Clean generated files"
	@echo "make run-api    - Start FastAPI server"
	@echo "make lint       - Run code linting"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf chroma_db/ demo_db/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-api:
	python -m src.api

lint:
	flake8 src/ --max-line-length=100
	black --check src/

format:
	black src/ tests/ examples/
