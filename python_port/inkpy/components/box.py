"""
Box component module.

Enhanced Box component with full styling support, ARIA, and BackgroundContext.
"""
from typing import Optional, Union, Any, Dict
from reactpy import component, html
from reactpy.core.hooks import use_context
from inkpy.components.accessibility_context import accessibility_context
from inkpy.components.background_context import background_context


@component
def Box(
    children=None,
    style: Optional[Dict[str, Any]] = None,
    backgroundColor: Optional[Union[str, int]] = None,
    borderStyle: Optional[str] = None,
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
        aria_label: Label for screen readers
        aria_hidden: Hide element from screen readers
        aria_role: ARIA role (button, checkbox, list, etc.)
        aria_state: ARIA state dictionary (checked, disabled, etc.)
        **kwargs: Additional props
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
    
    if children is None:
        children = []
    if style is None:
        style = {}
    
    # Merge style with defaults
    final_style = {
        'flexWrap': 'nowrap',
        'flexDirection': 'row',
        'flexGrow': 0,
        'flexShrink': 1,
        **style
    }
    
    # Add backgroundColor and borderStyle to style
    if backgroundColor:
        final_style['backgroundColor'] = backgroundColor
    
    if borderStyle:
        final_style['borderStyle'] = borderStyle
    
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
    
    # Add other kwargs
    attributes.update(kwargs)
    
    # Create box element
    box_element = html.div({
        **attributes,
        'children': children
    })
    
    # If backgroundColor is set, wrap with BackgroundContext Provider
    if backgroundColor:
        return background_context(
            box_element,
            value=backgroundColor
        )
    
    return box_element
