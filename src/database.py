"""ChromaDB vector database interface."""
import chromadb
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from .ingestion.chunker import CodeChunk
from .ingestion.embedder import Embedder
from .ingestion.graph import DependencyGraph


class CodebaseDB:
    """Vector database for code chunks."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = None
        self.embedder = Embedder()
        self.dependency_graph = DependencyGraph()
        self.graph_path = Path(self.persist_directory) / "dependency_graph.json"
        self.base_path = None  # Store base path for dependency resolution
        self._load_dependency_graph()

    def _normalize_file_path(self, file_path: str, base_path: Optional[Path]) -> str:
        """Normalize paths to be relative to the indexed repository when possible."""
        if not base_path:
            return str(file_path)

        path_obj = Path(file_path)
        try:
            if path_obj.is_absolute():
                return str(path_obj.resolve().relative_to(base_path.resolve()))
            return str(path_obj)
        except (ValueError, OSError):
            return str(file_path)

    def _save_dependency_graph(self):
        """Persist dependency graph so it survives process restarts."""
        try:
            graph_data = {
                "graph": {k: sorted(v) for k, v in self.dependency_graph.graph.items()}
            }
            with open(self.graph_path, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to persist dependency graph: {e}")

    def _load_dependency_graph(self):
        """Load persisted dependency graph if available."""
        if not self.graph_path.exists():
            return

        try:
            with open(self.graph_path, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            for from_file, to_files in graph_data.get("graph", {}).items():
                for to_file in to_files:
                    self.dependency_graph.add_dependency(from_file, to_file)
        except Exception as e:
            print(f"Warning: Failed to load dependency graph: {e}")
    
    def create_collection(self, name: str = "codebase"):
        """Create or get collection."""
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(self, chunks: List[CodeChunk], batch_size: int = 100, base_path: Optional[Path] = None):
        """Add code chunks to database."""
        if not self.collection:
            self.create_collection()
        
        if not chunks:
            return
        
        # Store base path for dependency resolution
        if base_path:
            self.base_path = Path(base_path).resolve()
        elif not self.base_path and chunks:
            # Infer base path from first chunk
            self.base_path = Path(chunks[0].file_path).parent.parent
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Prepare data
            documents = []
            metadatas = []
            ids = []
            
            for j, chunk in enumerate(batch):
                normalized_file_path = self._normalize_file_path(chunk.file_path, self.base_path)

                # Create searchable document (code + imports)
                doc = chunk.content
                if chunk.imports:
                    doc = "\n".join(chunk.imports) + "\n\n" + doc
                
                documents.append(doc)
                metadatas.append({
                    'file_path': normalized_file_path,
                    'language': chunk.language,
                    'chunk_type': chunk.chunk_type,
                    'name': chunk.name or '',
                    'start_line': chunk.start_line,
                    'end_line': chunk.end_line,
                    'imports': '|||'.join(chunk.imports)  # Store as string
                })
                # Use global counter to avoid ID collisions
                chunk_id = f"{normalized_file_path}:{chunk.start_line}:{chunk.end_line}:{i}:{j}"
                ids.append(chunk_id)
                
                # Build dependency graph with proper base path
                if chunk.imports and self.base_path:
                    self.dependency_graph.build_from_imports(
                        normalized_file_path, chunk.imports, self.base_path
                    )
            
            # Generate embeddings
            try:
                embeddings = self.embedder.embed_texts(documents)
            except Exception as e:
                print(f"Warning: Failed to generate embeddings for batch {i}: {e}")
                continue
            
            # Add to collection
            try:
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                print(f"Warning: Failed to add batch {i} to collection: {e}")

        self._save_dependency_graph()
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant code chunks."""
        if not self.collection:
            return []
        
        # Check if collection has any documents
        if self.collection.count() == 0:
            return []
        
        # Generate query embedding
        try:
            query_embedding = self.embedder.embed_single(query)
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return []
        
        # Search
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.collection.count()),
                where=filter_dict
            )
        except Exception as e:
            print(f"Error searching collection: {e}")
            return []
        
        # Check if results are empty
        if not results['ids'] or not results['ids'][0]:
            return []
        
        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            # Restore imports from string
            imports = metadata.get('imports', '').split('|||') if metadata.get('imports') else []
            metadata['imports'] = [imp for imp in imports if imp]
            
            formatted.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': metadata,
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.collection:
            return {}
        
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection.name
        }
    
    def clear(self):
        """Clear the database."""
        if self.collection:
            self.client.delete_collection(self.collection.name)
            self.collection = None
        self.dependency_graph.graph.clear()
        self.dependency_graph.reverse_graph.clear()
        self.base_path = None
        if self.graph_path.exists():
            try:
                self.graph_path.unlink()
            except Exception as e:
                print(f"Warning: Failed to remove dependency graph file: {e}")
