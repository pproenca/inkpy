"""
Tests for Box component snake_case style prop mapping.
"""
import pytest
from reactpy.core.layout import Layout
from inkpy.components.box import Box


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get('model') if isinstance(update, dict) else update


def _find_div_in_vdom(vdom):
    """Recursively find the div element in nested VDOM structure"""
    if not isinstance(vdom, dict):
        return None
    
    if vdom.get('tagName') == 'div':
        return vdom
    
    # Check children
    children = vdom.get('children', [])
    if isinstance(children, list):
        for child in children:
            result = _find_div_in_vdom(child)
            if result:
                return result
    elif isinstance(children, dict):
        return _find_div_in_vdom(children)
    
    return None


@pytest.mark.asyncio
async def test_box_snake_case_flex_direction():
    """Test Box converts flex_direction to flexDirection"""
    box_comp = Box(flex_direction="column")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('flexDirection') == "column"


@pytest.mark.asyncio
async def test_box_snake_case_align_items():
    """Test Box converts align_items to alignItems"""
    box_comp = Box(align_items="center")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('alignItems') == "center"


@pytest.mark.asyncio
async def test_box_snake_case_justify_content():
    """Test Box converts justify_content to justifyContent"""
    box_comp = Box(justify_content="space-between")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('justifyContent') == "space-between"


@pytest.mark.asyncio
async def test_box_snake_case_background_color():
    """Test Box converts background_color to backgroundColor"""
    box_comp = Box(background_color="blue")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('backgroundColor') == "blue"


@pytest.mark.asyncio
async def test_box_snake_case_border_style():
    """Test Box converts border_style to borderStyle"""
    box_comp = Box(border_style="single")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('borderStyle') == "single"


@pytest.mark.asyncio
async def test_box_snake_case_padding_props():
    """Test Box converts padding_* props to paddingTop, etc."""
    box_comp = Box(padding_top=1, padding_left=2)
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('paddingTop') == 1
    assert style.get('paddingLeft') == 2


@pytest.mark.asyncio
async def test_box_snake_case_margin_props():
    """Test Box converts margin_* props to marginTop, etc."""
    box_comp = Box(margin_top=1, margin_bottom=2)
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('marginTop') == 1
    assert style.get('marginBottom') == 2


@pytest.mark.asyncio
async def test_box_snake_case_flex_props():
    """Test Box converts flex_* props to flexGrow, etc."""
    box_comp = Box(flex_grow=1, flex_shrink=0)
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('flexGrow') == 1
    assert style.get('flexShrink') == 0


@pytest.mark.asyncio
async def test_box_snake_case_multiple_props():
    """Test Box converts multiple snake_case props at once"""
    box_comp = Box(
        flex_direction="column",
        align_items="center",
        justify_content="space-between",
        padding_top=1,
        margin_bottom=2
    )
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('flexDirection') == "column"
    assert style.get('alignItems') == "center"
    assert style.get('justifyContent') == "space-between"
    assert style.get('paddingTop') == 1
    assert style.get('marginBottom') == 2


@pytest.mark.asyncio
async def test_box_camelcase_still_works():
    """Test Box still accepts camelCase props"""
    box_comp = Box(backgroundColor="red", borderStyle="double")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('backgroundColor') == "red"
    assert style.get('borderStyle') == "double"


@pytest.mark.asyncio
async def test_box_snake_case_overrides_style_dict():
    """Test snake_case props override style dict values"""
    box_comp = Box(
        style={'flexDirection': 'row'},
        flex_direction="column"  # This should override
    )
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('flexDirection') == "column"

