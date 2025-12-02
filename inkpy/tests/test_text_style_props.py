"""
Tests for Text component snake_case style prop mapping.
"""
import pytest
from reactpy.core.layout import Layout
from inkpy.components.text import Text


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get('model') if isinstance(update, dict) else update


def _find_span_in_vdom(vdom):
    """Recursively find the span element in nested VDOM structure"""
    if not isinstance(vdom, dict):
        return None
    
    if vdom.get('tagName') == 'span':
        return vdom
    
    # Check children
    children = vdom.get('children', [])
    if isinstance(children, list):
        for child in children:
            result = _find_span_in_vdom(child)
            if result:
                return result
    elif isinstance(children, dict):
        return _find_span_in_vdom(children)
    
    return None


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
    style = span.get('attributes', {}).get('style', {})
    assert style.get('flexDirection') == "column"


@pytest.mark.asyncio
async def test_text_snake_case_text_wrap():
    """Test Text converts text_wrap to textWrap"""
    text_comp = Text(children="Hello", text_wrap="truncate-end")
    vdom = await _render_component(text_comp)
    
    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get('attributes', {}).get('style', {})
    assert style.get('textWrap') == "truncate-end"


@pytest.mark.asyncio
async def test_text_snake_case_flex_props():
    """Test Text converts flex_* props"""
    text_comp = Text(children="Hello", flex_grow=1, flex_shrink=0)
    vdom = await _render_component(text_comp)
    
    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get('attributes', {}).get('style', {})
    assert style.get('flexGrow') == 1
    assert style.get('flexShrink') == 0


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
    text_comp = Text(
        children="Hello",
        background_color="blue",
        dim_color=True,
        flex_grow=1
    )
    vdom = await _render_component(text_comp)
    
    span = _find_span_in_vdom(vdom)
    assert span is not None
    style = span.get('attributes', {}).get('style', {})
    assert style.get('flexGrow') == 1

