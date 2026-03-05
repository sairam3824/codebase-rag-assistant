"""FastAPI server for web interface."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .database import CodebaseDB
from .retrieval.reranker import Reranker
from .retrieval.context_builder import ContextBuilder
from .chat.engine import ChatEngine
from .ingestion.cloner import CodebaseLoader
from .ingestion.chunker import CodeChunker
from pathlib import Path

app = FastAPI(title="RAG Codebase Assistant API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
db = CodebaseDB()
chat_engine = ChatEngine()
context_builder = ContextBuilder()
reranker = Reranker()


class IndexRequest(BaseModel):
    source: str  # GitHub URL or local path
    collection_name: Optional[str] = "codebase"


class ChatRequest(BaseModel):
    query: str
    collection_name: Optional[str] = "codebase"


class ChatResponse(BaseModel):
    response: str
    sources: List[dict]


@app.post("/index")
async def index_codebase(request: IndexRequest):
    """Index a codebase."""
    try:
        loader = CodebaseLoader()
        chunker = CodeChunker()
        
        # Load codebase
        if request.source.startswith('http'):
            repo_path = loader.load_from_github(request.source)
        else:
            repo_path = Path(request.source)
        
        # Scan and chunk
        code_files = loader.scan_directory(repo_path)
        all_chunks = []
        
        for file_path in code_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                chunks = chunker.chunk_file(file_path, content)
                all_chunks.extend(chunks)
            except Exception:
                continue
        
        # Index
        db.create_collection(request.collection_name)
        db.add_chunks(all_chunks)
        
        stats = db.get_stats()
        return {
            "status": "success",
            "chunks_indexed": stats['total_chunks'],
            "collection": request.collection_name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_with_codebase(request: ChatRequest):
    """Chat with indexed codebase."""
    try:
        db.create_collection(request.collection_name)
        
        # Search
        results = db.search(request.query, n_results=20)
        results = reranker.rerank(request.query, results, top_k=5)
        
        # Build context and get response
        context = context_builder.build_context(request.query, results, db.dependency_graph)
        response = chat_engine.chat(request.query, context)
        
        # Format sources
        sources = [
            {
                "file": r['metadata']['file_path'],
                "name": r['metadata'].get('name', ''),
                "type": r['metadata']['chunk_type']
            }
            for r in results
        ]
        
        return ChatResponse(response=response, sources=sources)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    return db.get_stats()


@app.post("/clear")
async def clear_database():
    """Clear the database."""
    db.clear()
    chat_engine.clear_history()
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
