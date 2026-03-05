"""Tests for dependency graph."""
import pytest
from pathlib import Path
from src.ingestion.graph import DependencyGraph


def test_add_dependency():
    """Test adding dependencies."""
    graph = DependencyGraph()
    
    graph.add_dependency("a.py", "b.py")
    graph.add_dependency("a.py", "c.py")
    
    deps = graph.get_dependencies("a.py")
    assert "b.py" in deps
    assert "c.py" in deps


def test_reverse_dependencies():
    """Test getting dependents (reverse)."""
    graph = DependencyGraph()
    
    graph.add_dependency("a.py", "b.py")
    graph.add_dependency("c.py", "b.py")
    
    dependents = graph.get_dependents("b.py")
    assert "a.py" in dependents
    assert "c.py" in dependents


def test_transitive_dependents():
    """Test transitive dependency analysis."""
    graph = DependencyGraph()
    
    # a -> b -> c -> d
    graph.add_dependency("a.py", "b.py")
    graph.add_dependency("b.py", "c.py")
    graph.add_dependency("c.py", "d.py")
    
    # What would be affected if d.py changes?
    affected = graph.get_transitive_dependents("d.py")
    
    assert "c.py" in affected
    assert "b.py" in affected
    assert "a.py" in affected
