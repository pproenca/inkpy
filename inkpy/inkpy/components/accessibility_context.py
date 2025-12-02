"""
AccessibilityContext module - ReactPy context for accessibility settings
"""
from reactpy.core.hooks import create_context

# Default context value - dict with is_screen_reader_enabled flag
_default_value = {
    'is_screen_reader_enabled': False
}

# Create context with default value
accessibility_context = create_context(_default_value)

accessibility_context.__name__ = 'InternalAccessibilityContext'

