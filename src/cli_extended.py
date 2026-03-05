"""Extended CLI commands for advanced features."""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from .database import CodebaseDB
from .cache import SimpleCache
from .utils import format_file_size

console = Console()


@click.group()
def extended_cli():
    """Extended commands for RAG Codebase Assistant."""
    pass


@extended_cli.command()
@click.option('--db-path', default='./chroma_db', help='Database path')
def stats(db_path: str):
    """Show detailed database statistics."""
    db = CodebaseDB(persist_directory=db_path)
    db.create_collection()
    
    stats = db.get_stats()
    
    if stats.get('total_chunks', 0) == 0:
        console.print("[yellow]No indexed codebase found[/yellow]")
        return
    
    # Create stats table
    table = Table(title="Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Chunks", str(stats['total_chunks']))
    table.add_row("Collection Name", stats['collection_name'])
    table.add_row("Database Path", db_path)
    
    # Get dependency graph stats
    graph = db.dependency_graph
    total_deps = sum(len(deps) for deps in graph.graph.values())
    table.add_row("Total Dependencies", str(total_deps))
    table.add_row("Files in Graph", str(len(graph.graph)))
    
    console.print(table)


@extended_cli.command()
@click.argument('file_path')
@click.option('--db-path', default='./chroma_db', help='Database path')
def impact(file_path: str, db_path: str):
    """Analyze impact of changing a file."""
    db = CodebaseDB(persist_directory=db_path)
    db.create_collection()
    
    graph = db.dependency_graph
    
    # Get direct dependents
    direct = graph.get_dependents(file_path)
    
    # Get transitive dependents
    transitive = graph.get_transitive_dependents(file_path)
    
    console.print(Panel.fit(
        f"[bold cyan]Impact Analysis: {file_path}[/bold cyan]",
        border_style="cyan"
    ))
    
    if not direct and not transitive:
        console.print("[yellow]No dependencies found for this file[/yellow]")
        return
    
    console.print(f"\n[bold]Direct Dependents ({len(direct)}):[/bold]")
    for dep in sorted(direct):
        console.print(f"  • {dep}")
    
    console.print(f"\n[bold]All Affected Files ({len(transitive)}):[/bold]")
    for dep in sorted(transitive):
        console.print(f"  • {dep}")
    
    # Risk assessment
    risk = "LOW" if len(transitive) < 5 else "MEDIUM" if len(transitive) < 15 else "HIGH"
    color = "green" if risk == "LOW" else "yellow" if risk == "MEDIUM" else "red"
    console.print(f"\n[bold {color}]Risk Level: {risk}[/bold {color}]")


@extended_cli.command()
def cache_info():
    """Show cache information."""
    cache = SimpleCache()
    size = cache.get_size()
    
    console.print(Panel.fit(
        f"[bold cyan]Cache Information[/bold cyan]\n\n"
        f"Cache Directory: {cache.cache_dir}\n"
        f"Total Size: {format_file_size(size)}\n"
        f"TTL: {cache.ttl.total_seconds() / 3600:.1f} hours",
        border_style="cyan"
    ))


@extended_cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear the cache?')
def cache_clear():
    """Clear the cache."""
    cache = SimpleCache()
    cache.clear()
    console.print("[green]✓ Cache cleared[/green]")


@extended_cli.command()
@click.argument('query')
@click.option('--db-path', default='./chroma_db', help='Database path')
@click.option('--limit', default=10, help='Number of results')
def search(query: str, db_path: str, limit: int):
    """Search codebase without chat."""
    db = CodebaseDB(persist_directory=db_path)
    db.create_collection()
    
    results = db.search(query, n_results=limit)
    
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return
    
    console.print(f"\n[bold cyan]Found {len(results)} results:[/bold cyan]\n")
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        console.print(f"[bold]{i}. {metadata['file_path']}[/bold]")
        if metadata.get('name'):
            console.print(f"   {metadata['chunk_type']}: {metadata['name']}")
        console.print(f"   Lines {metadata['start_line']}-{metadata['end_line']}")
        console.print()


if __name__ == '__main__':
    extended_cli()
