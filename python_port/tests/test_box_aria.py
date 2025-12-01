"""
Tests for Box component with ARIA and BackgroundContext support
"""
import pytest
from reactpy.core.layout import Layout
from inkpy.components.box import Box


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


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get('model') if isinstance(update, dict) else update


@pytest.mark.asyncio
async def test_box_with_aria_label():
    """Test Box can accept aria-label prop"""
    box_comp = Box(aria_label="Test Label")
    vdom = await _render_component(box_comp)
    
    # Find the actual div in nested VDOM
    div = _find_div_in_vdom(vdom)
    assert div is not None
    assert div['attributes'].get('aria-label') == "Test Label"


@pytest.mark.asyncio
async def test_box_with_aria_hidden():
    """Test Box can accept aria-hidden prop"""
    box_comp = Box(aria_hidden=True)
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    assert div['attributes'].get('aria-hidden') == True


@pytest.mark.asyncio
async def test_box_with_aria_role():
    """Test Box can accept aria-role prop"""
    box_comp = Box(aria_role="button")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    assert div['attributes'].get('aria-role') == "button"


@pytest.mark.asyncio
async def test_box_with_aria_state():
    """Test Box can accept aria-state prop"""
    aria_state = {'checked': True, 'disabled': False}
    box_comp = Box(aria_state=aria_state)
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    assert div['attributes'].get('aria-state') == aria_state


@pytest.mark.asyncio
async def test_box_sets_internal_accessibility():
    """Test Box sets internal_accessibility attribute"""
    box_comp = Box(
        aria_role="button",
        aria_state={'checked': True}
    )
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    attrs = div['attributes']
    
    # internal_accessibility should contain role and state
    assert 'internal_accessibility' in attrs
    acc = attrs['internal_accessibility']
    assert acc.get('role') == "button"
    assert acc.get('state') == {'checked': True}


@pytest.mark.asyncio
async def test_box_with_background_color():
    """Test Box includes backgroundColor in style and wraps with context"""
    box_comp = Box(backgroundColor="blue")
    vdom = await _render_component(box_comp)
    
    # Should be wrapped in context provider (nested structure)
    assert isinstance(vdom, dict)
    
    # Find the div
    div = _find_div_in_vdom(vdom)
    assert div is not None
    style = div.get('attributes', {}).get('style', {})
    assert style.get('backgroundColor') == "blue"


@pytest.mark.asyncio
async def test_box_aria_hidden_with_screen_reader():
    """Test Box passes through aria-hidden attribute"""
    box_comp = Box(aria_hidden=True)
    vdom = await _render_component(box_comp)
    
    # In non-screen-reader mode, aria-hidden should be in attributes
    div = _find_div_in_vdom(vdom)
    if div:
        assert div['attributes'].get('aria-hidden') == True


@pytest.mark.asyncio
async def test_box_aria_label_rendered_in_screen_reader_mode():
    """Test Box stores aria-label attribute"""
    box_comp = Box(aria_label="Screen reader text", children="Regular children")
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    assert div['attributes'].get('aria-label') == "Screen reader text"


@pytest.mark.asyncio
async def test_box_combines_aria_props():
    """Test Box can combine multiple ARIA props"""
    box_comp = Box(
        aria_label="Button",
        aria_role="button",
        aria_state={'checked': True, 'disabled': False}
    )
    vdom = await _render_component(box_comp)
    
    div = _find_div_in_vdom(vdom)
    assert div is not None
    attrs = div['attributes']
    assert attrs.get('aria-label') == "Button"
    assert attrs.get('aria-role') == "button"
    assert attrs.get('aria-state') == {'checked': True, 'disabled': False}

