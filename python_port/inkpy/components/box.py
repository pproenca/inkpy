"""
Box component module.

Enhanced Box component with full styling support.
"""
from typing import Optional, Union, Any, Dict
from reactpy import component, html


@component
def Box(
    children=None,
    style: Optional[Dict[str, Any]] = None,
    backgroundColor: Optional[Union[str, int]] = None,
    borderStyle: Optional[str] = None,
    **kwargs
):
    """
    Box component with full styling support.
    
    Args:
        children: Child components
        style: Style dictionary (supports all flexbox properties)
        backgroundColor: Background color
        borderStyle: Border style ('single', 'double', 'round', 'bold', etc.)
        **kwargs: Additional props (aria-label, aria-role, aria-state, etc.)
    """
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
    
    return html.div({
        "style": final_style,
        "children": children,
        **kwargs
    })
