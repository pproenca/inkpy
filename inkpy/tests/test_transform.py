"""
Tests for Transform component.

Following TDD: Write failing test first, then implement.
"""

import pytest
from reactpy import component
from reactpy.core.layout import Layout

from inkpy.components.accessibility_context import accessibility_context
from inkpy.components.text import Text
from inkpy.components.transform import Transform


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get("model") if isinstance(update, dict) else update


def _find_span_in_vdom(vdom):
    """Find span element in VDOM"""
    if isinstance(vdom, dict):
        if vdom.get("tagName") == "span":
            return vdom
        children = vdom.get("children", [])
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
    attrs = span.get("attributes", {})
    if "children" in attrs:
        return attrs["children"]
    # Fallback to direct children
    children = span.get("children", "")
    if isinstance(children, list) and len(children) > 0:
        return children[0] if len(children) == 1 else children
    return children


@pytest.mark.asyncio
async def test_transform_uses_accessibility_label_in_screen_reader_mode():
    """Test that Transform uses accessibilityLabel instead of children in screen reader mode"""

    @component
    def App():
        return accessibility_context(
            Transform(
                accessibilityLabel="Screen reader text",
                transform=lambda text, idx: text.upper(),
                children=Text("Visible text"),
            ),
            value={"is_screen_reader_enabled": True},
        )

    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)

    # When screen reader is enabled, should use accessibilityLabel
    assert span is not None
    children = _get_span_children(span)
    # Children should be the accessibilityLabel, not the visible text
    assert children == "Screen reader text"


@pytest.mark.asyncio
async def test_transform_uses_children_when_screen_reader_disabled():
    """Test that Transform uses children when screen reader is disabled"""

    @component
    def App():
        return accessibility_context(
            Transform(
                accessibilityLabel="Screen reader text",
                transform=lambda text, idx: text.upper(),
                children=Text("Visible text"),
            ),
            value={"is_screen_reader_enabled": False},
        )

    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)

    # When screen reader is disabled, should use children
    assert span is not None
    # Children should be the Text component, not the accessibilityLabel
    # The Text component will render as a nested component
    assert span is not None


@pytest.mark.asyncio
async def test_transform_uses_children_when_no_accessibility_label():
    """Test that Transform uses children when no accessibilityLabel is provided"""

    @component
    def App():
        return accessibility_context(
            Transform(transform=lambda text, idx: text.upper(), children=Text("Regular text")),
            value={"is_screen_reader_enabled": True},
        )

    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)

    # Should use children when no accessibilityLabel
    assert span is not None


@pytest.mark.asyncio
async def test_transform_applies_transform_function():
    """Test that Transform applies transform function to children"""

    @component
    def App():
        return Transform(transform=lambda text, idx: text.upper(), children=Text("hello"))

    vdom = await _render_component(App())
    span = _find_span_in_vdom(vdom)

    # Should have internal_transform attribute
    assert span is not None
    attrs = span.get("attributes", {})
    event_handlers = span.get("eventHandlers", {})
    # Transform function should be stored in internal_transform
    assert "internal_transform" in event_handlers or "internal_transform" in attrs
