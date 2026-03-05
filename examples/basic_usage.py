"""Basic usage example for RAG Codebase Assistant."""
import os
from pathlib import Path
from src.ingestion.cloner import CodebaseLoader
from src.ingestion.chunker import CodeChunker
from src.database import CodebaseDB
from src.retrieval.reranker import Reranker
from src.retrieval.context_builder import ContextBuilder
from src.chat.engine import ChatEngine


def main():
    """Demonstrate basic usage."""
    # Set your OpenAI API key
    os.environ['OPENAI_API_KEY'] = 'your-key-here'
    
    # 1. Load codebase
    print("Loading codebase...")
    loader = CodebaseLoader()
    repo_path = loader.load_from_github("https://github.com/pallets/flask")
    
    # 2. Scan and chunk files
    print("Scanning files...")
    code_files = loader.scan_directory(repo_path)
    
    print("Chunking code...")
    chunker = CodeChunker()
    all_chunks = []
    
    for file_path in code_files[:10]:  # Limit to 10 files for demo
        try:
            content = file_path.read_text(encoding='utf-8')
            chunks = chunker.chunk_file(file_path, content)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Skipping {file_path}: {e}")
    
    print(f"Created {len(all_chunks)} chunks")
    
    # 3. Index to database
    print("Indexing to database...")
    db = CodebaseDB(persist_directory="./demo_db")
    db.create_collection("flask_demo")
    db.add_chunks(all_chunks)
    
    # 4. Query the codebase
    print("\nQuerying codebase...")
    query = "How does Flask routing work?"
    
    # Search
    results = db.search(query, n_results=10)
    
    # Re-rank
    reranker = Reranker()
    results = reranker.rerank(query, results, top_k=3)
    
    # Build context
    context_builder = ContextBuilder()
    context = context_builder.build_context(query, results)
    
    # Get answer
    chat_engine = ChatEngine()
    response = chat_engine.chat(query, context)
    
    print("\n" + "="*60)
    print(f"Question: {query}")
    print("="*60)
    print(response)
    print("="*60)


if __name__ == "__main__":
    main()
