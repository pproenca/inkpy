"""
Box component module.

Enhanced Box component with full styling support, ARIA, and BackgroundContext.
"""
from typing import Optional, Union, Any, Dict
from reactpy import component, html
from reactpy.core.hooks import use_context
from inkpy.components.accessibility_context import accessibility_context
from inkpy.components.background_context import background_context


# Style prop name mapping (snake_case -> camelCase)
STYLE_PROP_MAP = {
    'flex_direction': 'flexDirection',
    'align_items': 'alignItems',
    'align_content': 'alignContent',
    'align_self': 'alignSelf',
    'justify_content': 'justifyContent',
    'flex_wrap': 'flexWrap',
    'flex_grow': 'flexGrow',
    'flex_shrink': 'flexShrink',
    'flex_basis': 'flexBasis',
    'padding_top': 'paddingTop',
    'padding_bottom': 'paddingBottom',
    'padding_left': 'paddingLeft',
    'padding_right': 'paddingRight',
    'margin_top': 'marginTop',
    'margin_bottom': 'marginBottom',
    'margin_left': 'marginLeft',
    'margin_right': 'marginRight',
    'border_style': 'borderStyle',
    'border_color': 'borderColor',
    'background_color': 'backgroundColor',
    'min_width': 'minWidth',
    'min_height': 'minHeight',
    'max_width': 'maxWidth',
    'max_height': 'maxHeight',
    'overflow_x': 'overflowX',
    'overflow_y': 'overflowY',
    'text_wrap': 'textWrap',
}


def _normalize_style_props(kwargs: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Separate and normalize style props from other kwargs.
    
    Returns:
        Tuple of (style_props, other_kwargs)
    """
    style_props = {}
    other_kwargs = {}
    
    for key, value in kwargs.items():
        if key in STYLE_PROP_MAP:
            # Convert snake_case to camelCase
            camel_key = STYLE_PROP_MAP[key]
            style_props[camel_key] = value
        elif key in STYLE_PROP_MAP.values():
            # Already camelCase, pass through
            style_props[key] = value
        else:
            # Not a style prop
            other_kwargs[key] = value
    
    return style_props, other_kwargs


@component
def Box(
    children=None,
    style: Optional[Dict[str, Any]] = None,
    backgroundColor: Optional[Union[str, int]] = None,
    borderStyle: Optional[str] = None,
    # Snake_case aliases for common props
    background_color: Optional[Union[str, int]] = None,
    border_style: Optional[str] = None,
    aria_label: Optional[str] = None,
    aria_hidden: bool = False,
    aria_role: Optional[str] = None,
    aria_state: Optional[Dict[str, bool]] = None,
    **kwargs
):
    """
    Box component with full styling support, ARIA, and BackgroundContext.
    
    Args:
        children: Child components
        style: Style dictionary (supports all flexbox properties)
        backgroundColor: Background color (will provide via BackgroundContext)
        borderStyle: Border style ('single', 'double', 'round', 'bold', etc.)
        background_color: Snake_case alias for backgroundColor
        border_style: Snake_case alias for borderStyle
        aria_label: Label for screen readers
        aria_hidden: Hide element from screen readers
        aria_role: ARIA role (button, checkbox, list, etc.)
        aria_state: ARIA state dictionary (checked, disabled, etc.)
        **kwargs: Additional style props (snake_case or camelCase) and other attributes
    """
    # Get accessibility context (with default if not available)
    try:
        accessibility = use_context(accessibility_context)
        is_screen_reader_enabled = accessibility.get('is_screen_reader_enabled', False)
    except RuntimeError:
        # Context not available (e.g., in tests without Layout)
        is_screen_reader_enabled = False
    
    # Return None if hidden in screen reader mode
    if is_screen_reader_enabled and aria_hidden:
        return None
    
    # Determine effective children based on screen reader mode
    # When screen reader is enabled and aria_label is set, use aria_label as content
    if is_screen_reader_enabled and aria_label:
        effective_children = aria_label
    elif children is None:
        effective_children = []
    else:
        effective_children = children
    
    # Extract style props from kwargs (handles snake_case -> camelCase conversion)
    extra_style_props, other_kwargs = _normalize_style_props(kwargs)
    
    if style is None:
        style = {}
    
    # Merge style with defaults
    final_style = {
        'flexWrap': 'nowrap',
        'flexDirection': 'row',
        'flexGrow': 0,
        'flexShrink': 1,
        **style,
        **extra_style_props,  # Extra style props override style dict
    }
    
    # Handle snake_case aliases for explicit props
    effective_bg = backgroundColor or background_color
    effective_border = borderStyle or border_style
    
    # Add backgroundColor and borderStyle to style
    if effective_bg:
        final_style['backgroundColor'] = effective_bg
    
    if effective_border:
        final_style['borderStyle'] = effective_border
    
    # Handle overflow defaults
    if 'overflowX' not in final_style:
        final_style['overflowX'] = final_style.get('overflow', 'visible')
    if 'overflowY' not in final_style:
        final_style['overflowY'] = final_style.get('overflow', 'visible')
    
    # Build attributes dict
    attributes = {
        'style': final_style,
    }
    
    # Add ARIA attributes
    if aria_label is not None:
        attributes['aria-label'] = aria_label
    if aria_hidden:
        attributes['aria-hidden'] = aria_hidden
    if aria_role is not None:
        attributes['aria-role'] = aria_role
    if aria_state is not None:
        attributes['aria-state'] = aria_state
    
    # Set internal_accessibility for renderer
    if aria_role is not None or aria_state is not None:
        attributes['internal_accessibility'] = {
            'role': aria_role,
            'state': aria_state or {}
        }
    
    # Add other kwargs (non-style props)
    attributes.update(other_kwargs)
    
    # Create box element
    # Children must be passed as positional args, not in attributes dict
    # Otherwise ReactPy stringifies component objects instead of rendering them
    if effective_children is None or effective_children == []:
        box_element = html.div(attributes)
    elif isinstance(effective_children, (list, tuple)):
        box_element = html.div(attributes, *effective_children)
    else:
        box_element = html.div(attributes, effective_children)
    
    # If backgroundColor is set, wrap with BackgroundContext Provider
    if effective_bg:
        return background_context(
            box_element,
            value=effective_bg
        )
    
    return box_element
