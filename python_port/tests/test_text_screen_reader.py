"""
Tests for Text component screen reader support.

Following TDD: Write failing test first, then implement.
"""
import pytest
from reactpy import component
from reactpy.core.layout import Layout
from inkpy.components.text import Text
from inkpy.components.accessibility_context import accessibility_context


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get('model') if isinstance(update, dict) else update


def _find_span_in_vdom(vdom):
    """Find span element in VDOM"""
    if isinstance(vdom, dict):
        if vdom.get('tagName') == 'span':
            return vdom
        children = vdom.get('children', [])
        if isinstance(children, list):
            for child in children:
                result = _find_span_in_vdom(child)
                if result:
                    return result
        elif children:
            return _find_span_in_vdom(children)
    return None


def _get_span_children(span):
    """Get children from span element (can be in attributes or children)"""
    if not span:
        return None
    # Check attributes.children first (ReactPy stores it there)
    attrs = span.get('attributes', {})
    if 'children' in attrs:
        return attrs['children']
    # Fallback to direct children
    children = span.get('children', '')
    if isinstance(children, list) and len(children) > 0:
        return children[0] if len(children) == 1 else children
    return children


@pytest.mark.asyncio
async def test_text_uses_aria_label_in_screen_reader_mode():
    """Test that Text uses aria-label instead of children in screen reader mode"""
    @component
    def App():
        return accessibility_context(
            Text(aria_label="Screen reader text", children="Visible text"),
            value={'is_screen_reader_enabled': True}
        )
    
    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)
    
    # When screen reader is enabled, should use aria-label
    assert span is not None
    children = _get_span_children(span)
    # Children should be the aria-label, not the visible text
    assert children == "Screen reader text"


@pytest.mark.asyncio
async def test_text_uses_children_when_screen_reader_disabled():
    """Test that Text uses children when screen reader is disabled"""
    @component
    def App():
        return accessibility_context(
            Text(aria_label="Screen reader text", children="Visible text"),
            value={'is_screen_reader_enabled': False}
        )
    
    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)
    
    # When screen reader is disabled, should use children
    assert span is not None
    children = _get_span_children(span)
    assert children == "Visible text"


@pytest.mark.asyncio
async def test_text_hides_when_aria_hidden_in_screen_reader_mode():
    """Test that Text returns None when aria-hidden=True in screen reader mode"""
    @component
    def App():
        return accessibility_context(
            Text(aria_hidden=True, children="Hidden text"),
            value={'is_screen_reader_enabled': True}
        )
    
    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)
    
    # When screen reader is enabled and aria-hidden=True, should return None
    # This means the span should not be in the VDOM
    assert span is None


@pytest.mark.asyncio
async def test_text_shows_when_aria_hidden_but_screen_reader_disabled():
    """Test that Text shows normally when aria-hidden=True but screen reader is disabled"""
    @component
    def App():
        return accessibility_context(
            Text(aria_hidden=True, children="Visible text"),
            value={'is_screen_reader_enabled': False}
        )
    
    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)
    
    # When screen reader is disabled, aria-hidden should be ignored
    assert span is not None
    children = _get_span_children(span)
    assert children == "Visible text"


@pytest.mark.asyncio
async def test_text_uses_children_when_no_aria_label():
    """Test that Text uses children when no aria-label is provided, even in screen reader mode"""
    @component
    def App():
        return accessibility_context(
            Text(children="Regular text"),
            value={'is_screen_reader_enabled': True}
        )
    
    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)
    
    # Should use children when no aria-label
    assert span is not None
    children = _get_span_children(span)
    assert children == "Regular text"


@pytest.mark.asyncio
async def test_text_handles_none_children():
    """Test that Text returns None when children is None"""
    @component
    def App():
        return accessibility_context(
            Text(children=None),
            value={'is_screen_reader_enabled': False}
        )
    
    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)
    
    # Should return None when children is None
    assert span is None

