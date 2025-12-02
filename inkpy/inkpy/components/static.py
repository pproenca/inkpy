"""
Static component module.

Static component renders output once and persists above dynamic content.
"""
from typing import List, Optional, Callable, Any, Dict
from reactpy import component, use_state, use_effect
from .box import Box


@component
def Static(items: List[Any], children: Callable[[Any, int], Any], style: Optional[Dict[str, Any]] = None):
    """
    Static component that permanently renders output above everything else.
    
    Args:
        items: Array of items to render
        children: Function that renders each item: (item, index) -> component
        style: Styles to apply to container
    
    Example:
        @component
        def App():
            items = ["Task 1", "Task 2", "Task 3"]
            return Static(
                items=items,
                children=lambda item, idx: Text(f"{idx}: {item}")
            )
    """
    index, set_index = use_state(0)
    
    # Track items length to update index
    @use_effect
    def update_index():
        set_index(len(items))
    
    # Get items to render (new items since last render)
    items_to_render = items[index:]
    
    # Render children
    rendered_children = [children(item, index + idx) for idx, item in enumerate(items_to_render)]
    
    # Merge style with defaults
    final_style = {
        'position': 'absolute',
        'flexDirection': 'column',
        **(style or {})
    }
    
    return Box(style=final_style, internal_static=True, children=rendered_children)

