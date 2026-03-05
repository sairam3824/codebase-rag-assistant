"""Dependency graph builder for impact analysis."""
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict


class DependencyGraph:
    """Build and query dependency relationships between files."""
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def add_dependency(self, from_file: str, to_file: str):
        """Add a dependency edge."""
        self.graph[from_file].add(to_file)
        self.reverse_graph[to_file].add(from_file)
    
    def build_from_imports(self, file_path: str, imports: List[str], base_path: Path):
        """Extract dependencies from import statements."""
        for import_stmt in imports:
            resolved = self._resolve_import(import_stmt, file_path, base_path)
            if resolved:
                self.add_dependency(file_path, resolved)
    
    def _resolve_import(self, import_stmt: str, current_file: str, base_path: Path) -> Optional[str]:
        """Resolve import statement to file path."""
        try:
            # Python imports
            if 'import' in import_stmt:
                # from x.y import z or import x.y
                match = re.search(r'from\s+([\w.]+)|import\s+([\w.]+)', import_stmt)
                if match:
                    module = match.group(1) or match.group(2)
                    module_path = module.replace('.', '/')
                    
                    # Try to find the file
                    for ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                        potential = base_path / f"{module_path}{ext}"
                        if potential.exists():
                            try:
                                return str(potential.relative_to(base_path))
                            except ValueError:
                                # Path is outside base_path
                                continue
                    
                    # Try as directory with __init__.py
                    potential = base_path / module_path / '__init__.py'
                    if potential.exists():
                        try:
                            return str(potential.relative_to(base_path))
                        except ValueError:
                            pass
            
            # Relative imports (./file or ../file)
            if './' in import_stmt or '../' in import_stmt:
                match = re.search(r'["\']([^"\']+)["\']', import_stmt)
                if match:
                    rel_path = match.group(1)
                    current_dir = Path(current_file).parent
                    
                    # Resolve relative to base_path
                    try:
                        resolved = (base_path / current_dir / rel_path).resolve()
                        
                        if resolved.exists() and resolved.is_relative_to(base_path):
                            return str(resolved.relative_to(base_path))
                        
                        # Try with extensions
                        for ext in ['.js', '.ts', '.jsx', '.tsx', '.py']:
                            with_ext = resolved.with_suffix(ext)
                            if with_ext.exists() and with_ext.is_relative_to(base_path):
                                return str(with_ext.relative_to(base_path))
                    except (ValueError, OSError):
                        # Path resolution failed
                        pass
        except Exception:
            # Silently ignore resolution errors
            pass
        
        return None
    
    def get_dependencies(self, file_path: str) -> Set[str]:
        """Get files that this file depends on."""
        return self.graph.get(file_path, set())
    
    def get_dependents(self, file_path: str) -> Set[str]:
        """Get files that depend on this file (impact analysis)."""
        return self.reverse_graph.get(file_path, set())
    
    def get_transitive_dependents(self, file_path: str, max_depth: int = 3) -> Set[str]:
        """Get all files that would be affected by changes (transitive)."""
        visited = set()
        queue = [(file_path, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            
            visited.add(current)
            for dependent in self.get_dependents(current):
                if dependent not in visited:
                    queue.append((dependent, depth + 1))
        
        visited.discard(file_path)
        return visited
