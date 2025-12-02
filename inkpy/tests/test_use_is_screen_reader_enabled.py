"""
Tests for use_is_screen_reader_enabled hook
"""

import pytest
from reactpy import component
from reactpy.core.layout import Layout

from inkpy.components.accessibility_context import accessibility_context
from inkpy.hooks.use_is_screen_reader_enabled import use_is_screen_reader_enabled


async def _render_component(comp):
    """Helper to render a ReactPy component to VDOM via Layout"""
    layout = Layout(comp)
    async with layout:
        update = await layout.render()
        return update.get("model") if isinstance(update, dict) else update


@pytest.mark.asyncio
async def test_use_is_screen_reader_enabled_returns_false_by_default():
    """Test hook returns False when screen reader is not enabled"""
    result = {"value": None}

    @component
    def TestComponent():
        result["value"] = use_is_screen_reader_enabled()
        return None

    await _render_component(TestComponent())

    # Default should be False
    assert result["value"] is False


@pytest.mark.asyncio
async def test_use_is_screen_reader_enabled_reads_from_context():
    """Test hook reads value from AccessibilityContext"""
    result = {"value": None}

    @component
    def TestComponent():
        result["value"] = use_is_screen_reader_enabled()
        return None

    # Wrap with context provider
    @component
    def App():
        return accessibility_context(TestComponent(), value={"is_screen_reader_enabled": True})

    await _render_component(App())

    # Should read True from context
    assert result["value"] is True


@pytest.mark.asyncio
async def test_use_is_screen_reader_enabled_handles_false_context():
    """Test hook handles False value from context"""
    result = {"value": None}

    @component
    def TestComponent():
        result["value"] = use_is_screen_reader_enabled()
        return None

    @component
    def App():
        return accessibility_context(TestComponent(), value={"is_screen_reader_enabled": False})

    await _render_component(App())

    # Should read False from context
    assert result["value"] is False


@pytest.mark.asyncio
async def test_use_is_screen_reader_enabled_in_nested_context():
    """Test hook reads from nested context providers"""
    result = {"value": None}

    @component
    def TestComponent():
        result["value"] = use_is_screen_reader_enabled()
        return None

    @component
    def InnerApp():
        return accessibility_context(TestComponent(), value={"is_screen_reader_enabled": True})

    @component
    def OuterApp():
        return accessibility_context(
            InnerApp(),
            value={"is_screen_reader_enabled": False},  # Outer context
        )

    await _render_component(OuterApp())

    # Should read from inner (closest) context
    assert result["value"] is True
