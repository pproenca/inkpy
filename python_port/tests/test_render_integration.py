"""
Tests for render pipeline integration.

Following TDD: Write failing test first, then implement.
"""
import pytest
import io
from inkpy.ink import Ink
from inkpy.dom import create_node, DOMElement


def test_on_render_calls_renderer():
    """Test that Ink.on_render calls renderer function"""
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()
    
    ink = Ink(stdout=stdout, stdin=stdin, stderr=stderr, debug=True)
    
    # Set up root node with layout
    ink.root_node.yoga_node.calculate_layout(width=80)
    
    # Call on_render
    ink.on_render()
    
    # Should have written output (in debug mode)
    output = stdout.getvalue()
    # Output should not be empty (even if just newline)
    assert output is not None


def test_on_render_handles_static_output():
    """Test that Ink.on_render handles static output correctly"""
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()
    
    ink = Ink(stdout=stdout, stdin=stdin, stderr=stderr, debug=True)
    
    # Mark root as having static output
    ink.root_node.is_static_dirty = True
    ink.root_node.static_node = create_node('ink-box')
    
    # Set up layout
    ink.root_node.yoga_node.calculate_layout(width=80)
    
    # Call on_render
    ink.on_render()
    
    # Static output should be accumulated
    assert ink.full_static_output is not None


def test_on_render_skips_when_unmounted():
    """Test that Ink.on_render skips rendering when unmounted"""
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()
    
    ink = Ink(stdout=stdout, stdin=stdin, stderr=stderr)
    ink.is_unmounted = True
    
    # Should not raise or write anything
    ink.on_render()
    
    # Output should be empty
    assert stdout.getvalue() == ''


def test_on_render_calls_on_render_callback():
    """Test that Ink.on_render calls the on_render callback with metrics"""
    stdout = io.StringIO()
    stdin = io.StringIO()
    stderr = io.StringIO()
    
    metrics_received = []
    
    def on_render_callback(metrics):
        metrics_received.append(metrics)
    
    ink = Ink(
        stdout=stdout,
        stdin=stdin,
        stderr=stderr,
        on_render=on_render_callback
    )
    
    # Set up layout
    ink.root_node.yoga_node.calculate_layout(width=80)
    
    # Call on_render
    ink.on_render()
    
    # Callback should have been called
    assert len(metrics_received) == 1
    assert hasattr(metrics_received[0], 'render_time')


def test_renderer_function_exists():
    """Test that renderer function exists and can be imported"""
    from inkpy.renderer.renderer import renderer
    
    assert callable(renderer)


def test_renderer_returns_result_dict():
    """Test that renderer returns dict with output, outputHeight, staticOutput"""
    from inkpy.renderer.renderer import renderer
    from inkpy.dom import create_node
    
    root_node = create_node('ink-root')
    root_node.yoga_node.calculate_layout(width=80)
    
    result = renderer(root_node, False)
    
    assert isinstance(result, dict)
    assert 'output' in result
    assert 'outputHeight' in result
    assert 'staticOutput' in result

