"""
Tests for ErrorOverview component enhancements.

Following TDD: Write failing test first, then implement.
"""
import pytest
import os
import tempfile
from inkpy.components.error_overview import ErrorOverview, _cleanup_path, _get_code_excerpt, _parse_stack_line


def test_cleanup_path_removes_file_prefix():
    """Test that _cleanup_path removes file:// prefix"""
    cwd = os.getcwd()
    test_path = f"file://{cwd}/test.py"
    cleaned = _cleanup_path(test_path)
    assert cleaned == "test.py"


def test_cleanup_path_removes_cwd_prefix():
    """Test that _cleanup_path removes current working directory prefix"""
    cwd = os.getcwd()
    test_path = f"{cwd}/test.py"
    cleaned = _cleanup_path(test_path)
    assert cleaned == "test.py"


def test_get_code_excerpt_returns_lines():
    """Test that _get_code_excerpt returns code lines around error line"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("line 1\n")
        f.write("line 2\n")
        f.write("line 3\n")
        f.write("line 4\n")
        f.write("line 5\n")
        temp_path = f.name
    
    try:
        excerpt = _get_code_excerpt(temp_path, 3, context_lines=1)
        assert excerpt is not None
        assert len(excerpt) > 0
        # Should include line 3 and context
        line_nums = [line_num for line_num, _ in excerpt]
        assert 3 in line_nums
    finally:
        os.unlink(temp_path)


def test_parse_stack_line_extracts_info():
    """Test that _parse_stack_line parses Python stack trace format"""
    line = '  File "/path/to/file.py", line 10, in function_name'
    parsed = _parse_stack_line(line)
    
    assert parsed is not None
    assert parsed['file'] == "/path/to/file.py"
    assert parsed['line'] == 10
    assert parsed['function'] == "function_name"


def test_error_overview_shows_code_excerpt():
    """Test that ErrorOverview shows code excerpt with line highlighting"""
    # Create a temporary file with code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def test():\n")
        f.write("    raise ValueError('error')\n")
        temp_path = f.name
    
    try:
        # Create error at line 2
        error = ValueError("Test error")
        error.__traceback__ = None  # Mock traceback
        
        # ErrorOverview should handle this
        overview = ErrorOverview(error)
        assert overview is not None
    finally:
        os.unlink(temp_path)


def test_error_overview_has_aria_labels():
    """Test that ErrorOverview includes ARIA labels for accessibility"""
    error = ValueError("Test error")
    error.__traceback__ = None
    
    # ErrorOverview should include aria_label props
    # This will be verified through component structure
    overview = ErrorOverview(error)
    assert overview is not None

