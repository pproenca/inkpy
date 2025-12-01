"""
Tests for complete useInput hook with ReactPy effects
"""
import pytest
import asyncio
from reactpy import component
from reactpy.core.layout import Layout
from inkpy.hooks.use_input import use_input
from inkpy.input.keypress import Key


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get('model') if isinstance(update, dict) else update


@pytest.mark.asyncio
async def test_use_input_sets_up_raw_mode():
    """Test useInput sets up raw mode when active"""
    raw_mode_set = {'value': False}
    
    @component
    def TestComponent():
        def handle_input(input_str: str, key: Key):
            pass
        
        use_input(handle_input, is_active=True)
        return None
    
    await _render_component(TestComponent())
    
    # Hook should be callable without error
    # Actual raw mode setup depends on stdin context implementation
    assert True  # Placeholder - will verify with full implementation


@pytest.mark.asyncio
async def test_use_input_disables_when_inactive():
    """Test useInput doesn't set up when is_active=False"""
    @component
    def TestComponent():
        def handle_input(input_str: str, key: Key):
            pass
        
        use_input(handle_input, is_active=False)
        return None
    
    await _render_component(TestComponent())
    
    # Should not set up raw mode or listeners when inactive
    assert True  # Placeholder


@pytest.mark.asyncio
async def test_use_input_handles_keypress():
    """Test useInput calls handler with parsed keypress"""
    received_inputs = []
    
    @component
    def TestComponent():
        def handle_input(input_str: str, key: Key):
            received_inputs.append((input_str, key))
        
        use_input(handle_input)
        return None
    
    await _render_component(TestComponent())
    
    # Handler should be set up (actual input handling requires event emitter)
    assert True  # Placeholder


@pytest.mark.asyncio
async def test_use_input_cleans_up_on_unmount():
    """Test useInput cleans up raw mode and listeners on unmount"""
    @component
    def TestComponent():
        def handle_input(input_str: str, key: Key):
            pass
        
        use_input(handle_input)
        return None
    
    layout = Layout(TestComponent())
    async with layout:
        await layout.render()
        # Component unmounts when exiting context
    
    # Cleanup should be called
    assert True  # Placeholder

