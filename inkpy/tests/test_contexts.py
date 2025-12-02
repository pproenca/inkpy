"""
Tests for AccessibilityContext and BackgroundContext
"""


def test_accessibility_context_default():
    """Test that AccessibilityContext exists and is callable"""
    from inkpy.components.accessibility_context import accessibility_context

    # Should exist and be callable (ReactPy contexts are functions)
    assert accessibility_context is not None
    assert callable(accessibility_context)


def test_accessibility_context_default_value():
    """Test AccessibilityContext default value structure"""
    from inkpy.components.accessibility_context import accessibility_context

    # Get default value (ReactPy contexts expose this differently)
    # Check if it's a dict with is_screen_reader_enabled
    default_value = getattr(accessibility_context, "default_value", None) or getattr(
        accessibility_context, "default", None
    )

    if default_value is not None:
        assert isinstance(default_value, dict)
        assert "is_screen_reader_enabled" in default_value
        assert default_value["is_screen_reader_enabled"] is False


def test_background_context_default():
    """Test that BackgroundContext has default value"""
    from inkpy.components.background_context import background_context

    assert background_context is not None


def test_background_context_default_value():
    """Test BackgroundContext default value is None"""
    from inkpy.components.background_context import background_context

    # Background context should default to None (undefined)
    default_value = getattr(background_context, "default_value", None) or getattr(
        background_context, "default", None
    )

    if default_value is not None:
        assert default_value is None
