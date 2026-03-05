"""Build context from retrieved chunks for LLM."""
from typing import List, Dict, Any
import tiktoken


class ContextBuilder:
    """Assemble context from search results within token limits."""
    
    def __init__(self, model: str = "gpt-4", max_tokens: int = 8000):
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_tokens = max_tokens
    
    def build_context(
        self,
        query: str,
        results: List[Dict[str, Any]],
        dependency_graph: Any = None
    ) -> str:
        """
        Build context string from search results.
        
        Args:
            query: User query
            results: Search results with metadata
            dependency_graph: Optional dependency graph for related files
        
        Returns:
            Formatted context string
        """
        context_parts = []
        token_count = 0
        
        # Add file structure overview
        files = set(r['metadata'].get('file_path', '') for r in results)
        if files:
            structure = "## Relevant Files:\n" + "\n".join(f"- {f}" for f in sorted(files))
            context_parts.append(structure)
            token_count += len(self.encoding.encode(structure))
        
        # Add code chunks
        for i, result in enumerate(results):
            metadata = result['metadata']
            content = result['content']
            
            # Format chunk
            chunk_text = self._format_chunk(content, metadata, i + 1)
            chunk_tokens = len(self.encoding.encode(chunk_text))
            
            # Check token limit
            if token_count + chunk_tokens > self.max_tokens:
                break
            
            context_parts.append(chunk_text)
            token_count += chunk_tokens
            
            # Add import context if available
            imports = metadata.get('imports', [])
            if imports and token_count < self.max_tokens * 0.9:
                import_text = "\n".join(imports)
                import_tokens = len(self.encoding.encode(import_text))
                if token_count + import_tokens < self.max_tokens:
                    context_parts.append(f"Imports:\n{import_text}\n")
                    token_count += import_tokens
        
        return "\n\n".join(context_parts)
    
    def _format_chunk(self, content: str, metadata: Dict[str, Any], index: int) -> str:
        """Format a code chunk with metadata."""
        file_path = metadata.get('file_path', 'unknown')
        language = metadata.get('language', 'text')
        chunk_type = metadata.get('chunk_type', 'code')
        name = metadata.get('name', '')
        
        header = f"### [{index}] {file_path}"
        if name:
            header += f" - {chunk_type}: {name}"
        
        return f"{header}\n```{language}\n{content}\n```"
