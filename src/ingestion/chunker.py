"""Code-aware chunking using tree-sitter."""
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_java as tsjava
import tree_sitter_go as tsgo
import tree_sitter_rust as tsrust
import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_ruby as tsruby
from tree_sitter import Language, Parser, Node
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata."""
    content: str
    file_path: str
    language: str
    chunk_type: str  # 'function', 'class', 'method', 'file'
    name: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    imports: List[str] = None
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []


class CodeChunker:
    """Split code into semantic chunks respecting boundaries."""
    
    LANGUAGE_MAP = {
        '.py': ('python', tspython),
        '.js': ('javascript', tsjavascript),
        '.jsx': ('javascript', tsjavascript),
        '.ts': ('typescript', tstypescript),
        '.tsx': ('tsx', tstypescript),
        '.java': ('java', tsjava),
        '.go': ('go', tsgo),
        '.rs': ('rust', tsrust),
        '.c': ('c', tsc),
        '.cpp': ('cpp', tscpp),
        '.h': ('c', tsc),
        '.hpp': ('cpp', tscpp),
        '.rb': ('ruby', tsruby),
    }
    
    def __init__(self):
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        for ext, (lang_name, lang_module) in self.LANGUAGE_MAP.items():
            if lang_name not in self.parsers:
                parser = Parser()
                language = Language(lang_module.language())
                parser.set_language(language)
                self.parsers[lang_name] = parser
    
    def chunk_file(self, file_path: Path, content: str) -> List[CodeChunk]:
        """Chunk a file into semantic units."""
        ext = file_path.suffix
        if ext not in self.LANGUAGE_MAP:
            return self._fallback_chunk(file_path, content)
        
        lang_name, _ = self.LANGUAGE_MAP[ext]
        parser = self.parsers.get(lang_name)
        
        if not parser:
            return self._fallback_chunk(file_path, content)
        
        tree = parser.parse(bytes(content, 'utf8'))
        chunks = []
        
        # Extract imports
        imports = self._extract_imports(tree.root_node, content, lang_name)
        
        # Extract functions and classes
        chunks.extend(self._extract_definitions(
            tree.root_node, content, file_path, lang_name, imports
        ))
        
        return chunks if chunks else self._fallback_chunk(file_path, content)
    
    def _extract_imports(self, node: Node, content: str, language: str) -> List[str]:
        """Extract import statements."""
        imports = []
        import_types = {
            'python': ['import_statement', 'import_from_statement'],
            'javascript': ['import_statement'],
            'typescript': ['import_statement'],
            'tsx': ['import_statement'],
            'java': ['import_declaration'],
            'go': ['import_declaration'],
            'rust': ['use_declaration'],
        }
        
        types = import_types.get(language, [])
        for child in node.children:
            if child.type in types:
                imports.append(content[child.start_byte:child.end_byte])
        
        return imports
    
    def _extract_definitions(
        self, node: Node, content: str, file_path: Path,
        language: str, imports: List[str]
    ) -> List[CodeChunk]:
        """Extract function and class definitions."""
        chunks = []
        
        definition_types = {
            'python': ['function_definition', 'class_definition'],
            'javascript': ['function_declaration', 'class_declaration', 'method_definition'],
            'typescript': ['function_declaration', 'class_declaration', 'method_definition'],
            'tsx': ['function_declaration', 'class_declaration', 'method_definition'],
            'java': ['method_declaration', 'class_declaration'],
            'go': ['function_declaration', 'method_declaration'],
            'rust': ['function_item', 'impl_item'],
            'c': ['function_definition'],
            'cpp': ['function_definition', 'class_specifier'],
            'ruby': ['method', 'class'],
        }
        
        types = definition_types.get(language, [])
        
        def traverse(n: Node):
            if n.type in types:
                chunk_content = content[n.start_byte:n.end_byte]
                name = self._extract_name(n, content)
                
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=str(file_path),
                    language=language,
                    chunk_type=n.type,
                    name=name,
                    start_line=n.start_point[0],
                    end_line=n.end_point[0],
                    imports=imports.copy()
                ))
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return chunks
    
    def _extract_name(self, node: Node, content: str) -> Optional[str]:
        """Extract name from definition node."""
        for child in node.children:
            if 'identifier' in child.type or child.type == 'name':
                return content[child.start_byte:child.end_byte]
        return None
    
    def _fallback_chunk(self, file_path: Path, content: str) -> List[CodeChunk]:
        """Fallback to simple chunking for unsupported languages."""
        return [CodeChunk(
            content=content,
            file_path=str(file_path),
            language=file_path.suffix[1:],
            chunk_type='file',
            name=file_path.name
        )]
