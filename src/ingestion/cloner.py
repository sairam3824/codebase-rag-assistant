"""GitHub repository cloner and local directory scanner."""
import os
import tempfile
from pathlib import Path
from typing import List, Optional
from git import Repo
from rich.console import Console

console = Console()


class CodebaseLoader:
    """Load codebase from GitHub or local directory."""
    
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
        '.c', '.cpp', '.h', '.hpp', '.rb', '.php', '.cs', '.swift',
        '.kt', '.scala', '.sh', '.bash'
    }
    
    IGNORE_DIRS = {
        'node_modules', '.git', '__pycache__', 'venv', 'env',
        '.venv', 'dist', 'build', 'target', '.next', 'out'
    }
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix='rag_code_')
    
    def load_from_github(self, repo_url: str) -> Path:
        """Clone GitHub repository and return path."""
        console.print(f"[cyan]Cloning repository: {repo_url}[/cyan]")
        
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        clone_path = Path(self.temp_dir) / repo_name
        
        if clone_path.exists():
            console.print(f"[yellow]Repository already cloned at {clone_path}[/yellow]")
            return clone_path
        
        Repo.clone_from(repo_url, clone_path, depth=1)
        console.print(f"[green]✓ Cloned to {clone_path}[/green]")
        return clone_path
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory for code files."""
        directory = Path(directory)
        code_files = []
        
        for root, dirs, files in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.SUPPORTED_EXTENSIONS:
                    code_files.append(file_path)
        
        console.print(f"[green]Found {len(code_files)} code files[/green]")
        return code_files
