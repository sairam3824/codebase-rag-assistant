"""Example: Impact analysis using dependency graph."""
from pathlib import Path
from src.ingestion.graph import DependencyGraph


def analyze_impact():
    """Demonstrate impact analysis."""
    # Build a sample dependency graph
    graph = DependencyGraph()
    
    # Simulate a project structure
    graph.add_dependency("app/main.py", "app/auth.py")
    graph.add_dependency("app/main.py", "app/routes.py")
    graph.add_dependency("app/routes.py", "app/models.py")
    graph.add_dependency("app/auth.py", "app/models.py")
    graph.add_dependency("tests/test_auth.py", "app/auth.py")
    
    # Analyze: What would break if we change models.py?
    file_to_change = "app/models.py"
    affected = graph.get_transitive_dependents(file_to_change)
    
    print(f"Impact Analysis: Changing {file_to_change}")
    print("="*50)
    print(f"\nDirectly affected files:")
    for dep in graph.get_dependents(file_to_change):
        print(f"  - {dep}")
    
    print(f"\nAll affected files (transitive):")
    for dep in sorted(affected):
        print(f"  - {dep}")
    
    print(f"\nTotal files affected: {len(affected)}")


if __name__ == "__main__":
    analyze_impact()
