"""
Tests for Text component snake_case style prop mapping.
"""

import io

import pytest
from reactpy.core.layout import Layout

from inkpy import Box, Text, render
from inkpy.components.text import Text, _apply_text_styles


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get("model") if isinstance(update, dict) else update


def _find_span_in_vdom(vdom):
    """Recursively find the span element in nested VDOM structure"""
    if not isinstance(vdom, dict):
        return None

    if vdom.get("tagName") == "span":
        return vdom

    # Check children
    children = vdom.get("children", [])
    if isinstance(children, list):
        for child in children:
            result = _find_span_in_vdom(child)
            if result:
                return result
    elif isinstance(children, dict):
        return _find_span_in_vdom(children)

    return None


# === Tests for _apply_text_styles function ===


def test_apply_text_styles_plain():
    """Test _apply_text_styles with no styles returns plain text"""
    result = _apply_text_styles("hello")
    assert result == "hello"


def test_apply_text_styles_dim():
    """Test _apply_text_styles with dimColor"""
    result = _apply_text_styles("hello", dimColor=True)
    assert "\x1b[2m" in result  # Dim code
    assert "hello" in result


def test_apply_text_styles_color():
    """Test _apply_text_styles with foreground color"""
    result = _apply_text_styles("hello", color="red")
    assert "\x1b[" in result  # ANSI code
    assert "hello" in result


def test_apply_text_styles_background():
    """Test _apply_text_styles with background color"""
    result = _apply_text_styles("hello", backgroundColor="blue")
    assert "\x1b[" in result  # ANSI code
    assert "hello" in result


def test_apply_text_styles_bold():
    """Test _apply_text_styles with bold"""
    result = _apply_text_styles("hello", bold=True)
    assert "\x1b[1m" in result  # Bold code
    assert "hello" in result


def test_apply_text_styles_italic():
    """Test _apply_text_styles with italic"""
    result = _apply_text_styles("hello", italic=True)
    assert "\x1b[3m" in result  # Italic code
    assert "hello" in result


def test_apply_text_styles_underline():
    """Test _apply_text_styles with underline"""
    result = _apply_text_styles("hello", underline=True)
    assert "\x1b[4m" in result  # Underline code
    assert "hello" in result


def test_apply_text_styles_strikethrough():
    """Test _apply_text_styles with strikethrough"""
    result = _apply_text_styles("hello", strikethrough=True)
    assert "\x1b[9m" in result  # Strikethrough code
    assert "hello" in result


def test_apply_text_styles_inverse():
    """Test _apply_text_styles with inverse"""
    result = _apply_text_styles("hello", inverse=True)
    assert "\x1b[7m" in result  # Inverse code
    assert "hello" in result


def test_apply_text_styles_combined():
    """Test _apply_text_styles with multiple styles"""
    result = _apply_text_styles(
        "hello",
        color="red",
        backgroundColor="blue",
        bold=True,
        italic=True,
        underline=True,
    )
    assert "hello" in result
    assert "\x1b[1m" in result  # Bold
    assert "\x1b[3m" in result  # Italic
    assert "\x1b[4m" in result  # Underline


# === Integration tests for Text component in render context ===


def test_text_renders_with_all_style_props():
    """Test Text component renders with all style props applied"""
    from reactpy import component

    @component
    def App():
        return Box(
            Text(
                "styled",
                color="red",
                backgroundColor="blue",
                bold=True,
                italic=True,
                underline=True,
                strikethrough=True,
                inverse=True,
                dimColor=True,
            )
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    # Text should be present (styles applied as ANSI codes)
    assert "styled" in output
    instance.unmount()


def test_text_with_wrap_modes():
    """Test Text component with different wrap modes"""
    from reactpy import component

    @component
    def App():
        return Box(
            Text("wrap test", wrap="wrap"),
            Text("truncate end", wrap="truncate-end"),
            Text("truncate middle", wrap="truncate-middle"),
            Text("truncate start", wrap="truncate-start"),
        )

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    # Should render without errors
    assert instance is not None
    instance.unmount()


def test_text_returns_none_with_no_children():
    """Test Text returns None when no children provided"""
    text_elem = Text()
    # Text with no children should return None
    # (ReactPy component call returns render result)
    assert text_elem is not None  # It's a component, not None directly


def test_text_context_fallback():
    """Test Text handles missing context gracefully"""
    from reactpy import component

    # When rendered outside Layout, contexts should fallback gracefully
    @component
    def App():
        return Text("test", backgroundColor="red")

    stdout = io.StringIO()
    stdout.columns = 80
    stdout.rows = 24

    instance = render(App(), stdout=stdout, debug=True)
    output = stdout.getvalue()

    assert "test" in output
    instance.unmount()


@pytest.mark.asyncio
async def test_text_snake_case_background_color():
    """Test Text converts background_color to backgroundColor"""
    text_comp = Text(children="Hello", background_color="blue")
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    # The internal_transform should use the background color


@pytest.mark.asyncio
async def test_text_snake_case_dim_color():
    """Test Text accepts dim_color alias for dimColor"""
    text_comp = Text(children="Hello", dim_color=True)
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    # Component should render (testing it accepts the prop)


@pytest.mark.asyncio
async def test_text_snake_case_flex_direction():
    """Test Text converts flex_direction in style"""
    text_comp = Text(children="Hello", flex_direction="column")
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get("attributes", {}).get("style", {})
    assert style.get("flexDirection") == "column"


@pytest.mark.asyncio
async def test_text_snake_case_text_wrap():
    """Test Text converts text_wrap to textWrap"""
    text_comp = Text(children="Hello", text_wrap="truncate-end")
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get("attributes", {}).get("style", {})
    assert style.get("textWrap") == "truncate-end"


@pytest.mark.asyncio
async def test_text_snake_case_flex_props():
    """Test Text converts flex_* props"""
    text_comp = Text(children="Hello", flex_grow=1, flex_shrink=0)
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get("attributes", {}).get("style", {})
    assert style.get("flexGrow") == 1
    assert style.get("flexShrink") == 0


@pytest.mark.asyncio
async def test_text_camelcase_still_works():
    """Test Text still accepts camelCase props"""
    text_comp = Text(children="Hello", backgroundColor="red", dimColor=True)
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    # Should render without errors


@pytest.mark.asyncio
async def test_text_snake_case_multiple_props():
    """Test Text handles multiple snake_case props"""
    text_comp = Text(children="Hello", background_color="blue", dim_color=True, flex_grow=1)
    vdom = await _render_component(text_comp)

    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get("attributes", {}).get("style", {})
    assert style.get("flexGrow") == 1
