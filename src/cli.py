"""Command-line interface for RAG Codebase Assistant."""
import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown
from .ingestion.cloner import CodebaseLoader
from .ingestion.chunker import CodeChunker
from .database import CodebaseDB
from .retrieval.hybrid_search import HybridSearcher
from .retrieval.reranker import Reranker
from .retrieval.context_builder import ContextBuilder
from .chat.engine import ChatEngine

console = Console()


@click.group()
def cli():
    """RAG Codebase Assistant - Chat with any codebase."""
    pass


@cli.command()
@click.argument('source')
@click.option('--db-path', default='./chroma_db', help='Database path')
def index(source: str, db_path: str):
    """Index a codebase from GitHub URL or local directory."""
    console.print(Panel.fit(
        "[bold cyan]RAG Codebase Assistant[/bold cyan]\n"
        "Indexing codebase...",
        border_style="cyan"
    ))
    
    try:
        loader = CodebaseLoader()
        chunker = CodeChunker()
        db = CodebaseDB(persist_directory=db_path)
        
        # Load codebase
        if source.startswith('http'):
            repo_path = loader.load_from_github(source)
        else:
            repo_path = Path(source).resolve()
            if not repo_path.exists():
                console.print(f"[red]Error: Directory {source} does not exist[/red]")
                return
        
        # Scan files
        code_files = loader.scan_directory(repo_path)
        
        if not code_files:
            console.print("[yellow]Warning: No code files found[/yellow]")
            return
        
        # Chunk files
        all_chunks = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Chunking files...", total=len(code_files))
            
            for file_path in code_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    chunks = chunker.chunk_file(file_path, content)
                    all_chunks.extend(chunks)
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to process {file_path}: {e}[/yellow]")
        
        if not all_chunks:
            console.print("[red]Error: No code chunks created[/red]")
            return
        
        console.print(f"[green]✓ Created {len(all_chunks)} code chunks[/green]")
        
        # Index chunks with base path
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Indexing to vector database...", total=None)
            db.add_chunks(all_chunks, base_path=repo_path)
            progress.update(task, completed=True)
        
        stats = db.get_stats()
        console.print(Panel.fit(
            f"[bold green]✓ Indexing Complete[/bold green]\n\n"
            f"Total chunks: {stats['total_chunks']}\n"
            f"Database: {db_path}",
            border_style="green"
        ))
    
    except Exception as e:
        console.print(f"[red]Error during indexing: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@cli.command()
@click.option('--db-path', default='./chroma_db', help='Database path')
def chat(db_path: str):
    """Start interactive chat mode."""
    console.print(Panel.fit(
        "[bold cyan]RAG Codebase Assistant - Chat Mode[/bold cyan]\n"
        "Type your questions. Use 'exit' or 'quit' to leave.",
        border_style="cyan"
    ))
    
    try:
        # Initialize components
        db = CodebaseDB(persist_directory=db_path)
        db.create_collection()
        
        stats = db.get_stats()
        if stats.get('total_chunks', 0) == 0:
            console.print("[red]Error: No indexed codebase found. Run 'index' first.[/red]")
            return
        
        console.print(f"[green]Loaded database with {stats['total_chunks']} chunks[/green]\n")
        
        chat_engine = ChatEngine()
        context_builder = ContextBuilder()
        reranker = Reranker()
        
        while True:
            try:
                query = console.input("[bold cyan]You:[/bold cyan] ")
                
                if query.lower() in ['exit', 'quit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if not query.strip():
                    continue
                
                # Search
                with console.status("[cyan]Searching codebase...[/cyan]"):
                    results = db.search(query, n_results=20)
                    
                    if not results:
                        console.print("[yellow]No relevant code found. Try a different query.[/yellow]")
                        continue
                    
                    # Re-rank
                    results = reranker.rerank(query, results, top_k=5)
                    
                    # Build context
                    context = context_builder.build_context(query, results, db.dependency_graph)
                
                # Get response
                console.print("\n[bold green]Assistant:[/bold green]")
                response = chat_engine.chat(query, context)
                
                # Display with markdown
                md = Markdown(response)
                console.print(md)
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    except Exception as e:
        console.print(f"[red]Failed to initialize chat: {e}[/red]")


@cli.command()
@click.argument('question')
@click.option('--db-path', default='./chroma_db', help='Database path')
def ask(question: str, db_path: str):
    """Ask a single question."""
    db = CodebaseDB(persist_directory=db_path)
    db.create_collection()
    
    chat_engine = ChatEngine()
    context_builder = ContextBuilder()
    reranker = Reranker()
    
    # Search and answer
    results = db.search(question, n_results=20)
    results = reranker.rerank(question, results, top_k=5)
    context = context_builder.build_context(question, results, db.dependency_graph)
    
    response = chat_engine.chat(question, context)
    
    console.print(Panel.fit(
        Markdown(response),
        title="[bold cyan]Answer[/bold cyan]",
        border_style="cyan"
    ))


if __name__ == '__main__':
    cli()
