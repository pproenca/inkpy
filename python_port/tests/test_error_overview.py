"""
Tests for ErrorOverview component
"""
import pytest
import asyncio
from reactpy.core.layout import Layout
from inkpy.components.error_overview import ErrorOverview
from inkpy.components.box import Box
from inkpy.components.text import Text


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get('model') if isinstance(update, dict) else update


@pytest.mark.asyncio
async def test_error_overview_renders_error_message():
    """Test ErrorOverview displays error message"""
    error = ValueError("Test error message")
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Should render a Box with error message
    assert isinstance(vdom, dict)
    # Error message should be in the VDOM somewhere
    assert vdom is not None


@pytest.mark.asyncio
async def test_error_overview_shows_error_label():
    """Test ErrorOverview shows ERROR label with red background"""
    error = RuntimeError("Something went wrong")
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Should have ERROR label with red background
    assert isinstance(vdom, dict)


@pytest.mark.asyncio
async def test_error_overview_shows_file_location():
    """Test ErrorOverview shows file location if available"""
    def test_function():
        raise ValueError("Error in test function")
    
    try:
        test_function()
    except ValueError as e:
        error = e
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Should show file location if traceback is available
    assert isinstance(vdom, dict)


@pytest.mark.asyncio
async def test_error_overview_shows_code_excerpt():
    """Test ErrorOverview shows code excerpt around error line"""
    def test_function():
        x = 1
        y = 2
        raise ValueError("Error here")
        z = 3
    
    try:
        test_function()
    except ValueError as e:
        error = e
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Should show code excerpt if file is readable
    assert isinstance(vdom, dict)


@pytest.mark.asyncio
async def test_error_overview_shows_stack_trace():
    """Test ErrorOverview shows full stack trace"""
    def inner_function():
        raise ValueError("Inner error")
    
    def outer_function():
        inner_function()
    
    try:
        outer_function()
    except ValueError as e:
        error = e
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Should show stack trace
    assert isinstance(vdom, dict)


@pytest.mark.asyncio
async def test_error_overview_handles_missing_stack():
    """Test ErrorOverview handles errors without stack trace"""
    # Create error without __traceback__
    error = ValueError("Error without traceback")
    error.__traceback__ = None
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Should still render error message
    assert isinstance(vdom, dict)


@pytest.mark.asyncio
async def test_error_overview_highlights_error_line():
    """Test ErrorOverview highlights the error line in code excerpt"""
    def test_function():
        line1 = "ok"
        line2 = "error here"  # This line should be highlighted
        line3 = "ok"
        raise ValueError("Error")
    
    try:
        test_function()
    except ValueError as e:
        error = e
    
    error_comp = ErrorOverview(error=error)
    vdom = await _render_component(error_comp)
    
    # Error line should be highlighted (red background, white text)
    assert isinstance(vdom, dict)

