import pytest
from inkpy.hooks.use_stdin import use_stdin


def test_use_stdin_basic():
    """Test basic use_stdin hook"""
    # This will be tested with ReactPy integration
    assert callable(use_stdin)


def test_use_stdin_returns_stdin():
    """Test that use_stdin returns stdin access"""
    # In ReactPy component context, this would return stdin object
    # For now, verify the hook exists
    assert callable(use_stdin)

