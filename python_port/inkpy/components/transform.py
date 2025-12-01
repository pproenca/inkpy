"""
Transform component module.

Transform string representation of components before rendering.
"""
from typing import Optional, Callable, Any
from reactpy import component, html
from .text import Text


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
        accessibilityLabel: Screen-reader-specific text
    
    Example:
        Transform(
            children=Text("Hello"),
            transform=lambda text, idx: text.upper()
        )
    """
    if children is None:
        return None
    
    style = {
        'flexGrow': 0,
        'flexShrink': 1,
        'flexDirection': 'row'
    }
    
    return html.span({
        "style": style,
        "children": children,
        "internal_transform": transform
    })

