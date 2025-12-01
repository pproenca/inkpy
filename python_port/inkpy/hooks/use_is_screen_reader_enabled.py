"""
use_is_screen_reader_enabled hook - Returns whether a screen reader is enabled.
"""
from reactpy.core.hooks import use_context
from inkpy.components.accessibility_context import accessibility_context


def use_is_screen_reader_enabled() -> bool:
    """
    Returns whether a screen reader is enabled.
    
    This is useful when you want to render different output for screen readers.
    
    Returns:
        True if screen reader is enabled, False otherwise
    """
    try:
        ctx = use_context(accessibility_context)
        return ctx.get('is_screen_reader_enabled', False)
    except RuntimeError:
        # Context not available (e.g., in tests without Layout)
        return False

