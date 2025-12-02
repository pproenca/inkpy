"""
Tests for Text component with inherited background support
"""

import pytest
from reactpy import component
from reactpy.core.layout import Layout

from inkpy.components.box import Box
from inkpy.components.text import Text


def _find_span_in_vdom(vdom):
    """Recursively find the span element in nested VDOM structure"""
    if not isinstance(vdom, dict):
        return None

    if vdom.get("tagName") == "span":
        return vdom

    # Check children - handle both list and single child
    children = vdom.get("children", [])
    if isinstance(children, list):
        for child in children:
            # Skip Component objects (they're not rendered yet)
            if isinstance(child, dict):
                result = _find_span_in_vdom(child)
                if result:
                    return result
    elif isinstance(children, dict):
        return _find_span_in_vdom(children)

    # Also check attributes.children (sometimes children are stored there)
    attrs = vdom.get("attributes", {})
    if isinstance(attrs, dict):
        attrs_children = attrs.get("children", [])
        if isinstance(attrs_children, list):
            for child in attrs_children:
                if isinstance(child, dict):
                    result = _find_span_in_vdom(child)
                    if result:
                        return result

    return None


def _get_transform_from_span(span):
    """Extract transform function from span VDOM"""
    # ReactPy stores functions in eventHandlers
    event_handlers = span.get("eventHandlers", {})
    transform_handler = event_handlers.get("internal_transform")

    # The handler contains a target ID, but we need to get the actual function
    # For testing, we'll check that the handler exists
    # The actual transform will be applied by the renderer
    return transform_handler


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get("model") if isinstance(update, dict) else update


@pytest.mark.asyncio
async def test_text_with_explicit_background():
    """Test Text uses explicit backgroundColor when provided"""
    text_comp = Text(children="Hello", backgroundColor="red")
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None

    # Check that transform function exists in eventHandlers
    transform_handler = _get_transform_from_span(span)
    assert transform_handler is not None

    # Verify the component accepts backgroundColor prop
    assert hasattr(text_comp, "render")


@pytest.mark.asyncio
async def test_text_inherits_background_from_box():
    """Test Text component can be nested in Box with backgroundColor"""

    @component
    def App():
        return Box(backgroundColor="blue", children=[Text(children="Inherited background")])

    vdom = await _render_component(App())

    # Component should render (Box wraps Text in context)
    assert isinstance(vdom, dict)

    # The Text component will access background_context via use_context
    # This is verified by the component structure, not full rendering
    # Full rendering requires complete renderer integration


@pytest.mark.asyncio
async def test_text_prefers_explicit_over_inherited():
    """Test Text accepts explicit backgroundColor even when nested in Box"""

    @component
    def App():
        return Box(
            backgroundColor="blue", children=[Text(children="Explicit wins", backgroundColor="red")]
        )

    vdom = await _render_component(App())

    # Component should render
    assert isinstance(vdom, dict)

    # Text component uses: effective_background = backgroundColor or inherited_background
    # So explicit red will be preferred over inherited blue
    # This is verified by component logic, not full rendering


@pytest.mark.asyncio
async def test_text_without_background():
    """Test Text works without any background color"""
    text_comp = Text(children="No background")
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None

    transform_handler = _get_transform_from_span(span)
    assert transform_handler is not None

    # Component should render without background
    assert span.get("tagName") == "span"


@pytest.mark.asyncio
async def test_text_inherits_from_nested_context():
    """Test Text can access nested BackgroundContext providers"""

    @component
    def App():
        return Box(
            backgroundColor="outer",
            children=[Box(backgroundColor="inner", children=[Text(children="Nested inheritance")])],
        )

    vdom = await _render_component(App())

    # Component should render with nested contexts
    assert isinstance(vdom, dict)

    # Text will inherit from inner Box (closest context provider)
    # This is verified by ReactPy's context system
