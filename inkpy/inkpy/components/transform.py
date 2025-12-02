"""
Transform component module.

Transform string representation of components before rendering.
"""
from typing import Optional, Callable, Any
from reactpy import component, html
from reactpy.core.hooks import use_context
from .accessibility_context import accessibility_context


@component
def Transform(
    children: Any,
    transform: Callable[[str, int], str],
    accessibilityLabel: Optional[str] = None
):
    """
    Transform component output before rendering.
    
    Args:
        children: Child components to transform
        transform: Function that transforms text: (text, index) -> transformed_text
        accessibilityLabel: Screen-reader-specific text (shown when screen reader enabled)
    
    Example:
        Transform(
            children=Text("Hello"),
            transform=lambda text, idx: text.upper()
        )
    """
    if children is None:
        return None
    
    # Get accessibility context
    try:
        accessibility_ctx = use_context(accessibility_context)
        is_screen_reader_enabled = accessibility_ctx.get('is_screen_reader_enabled', False)
    except RuntimeError:
        # Context not available (e.g., in tests without Layout)
        is_screen_reader_enabled = False
    
    # Use accessibilityLabel when screen reader is enabled, otherwise use children
    children_or_label = (
        accessibilityLabel if (is_screen_reader_enabled and accessibilityLabel) else children
    )
    
    style = {
        'flexGrow': 0,
        'flexShrink': 1,
        'flexDirection': 'row'
    }
    
    return html.span({
        "style": style,
        "children": children_or_label,
        "internal_transform": transform
    })

