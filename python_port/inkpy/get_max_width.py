"""
Get Max Width - Calculate maximum content width for a Yoga node.

Ported from: src/get-max-width.ts
"""
from inkpy.layout.yoga_node import YogaNode
from poga.libpoga_capi import YGNodeLayoutGetPadding, YGNodeLayoutGetBorder, YGEdge


def get_max_width(yoga_node: YogaNode) -> float:
    """
    Calculate the maximum content width for a Yoga node,
    accounting for padding and borders.
    
    This is the width available for content after subtracting
    padding and border widths from the total computed width.
    
    Args:
        yoga_node: The Yoga node to calculate width for
        
    Returns:
        Maximum content width in pixels/characters
    """
    layout = yoga_node.get_layout()
    width = layout.get('width', 0)
    
    # Get computed padding and border from the underlying Yoga node
    # After layout calculation, these are the actual computed values
    poga_layout = yoga_node.view.poga_layout()
    
    # Access the underlying Yoga node (private attribute, but necessary for computed values)
    node_ref = poga_layout._PogaLayout__node
    
    # Get computed padding (left and right)
    padding_left = YGNodeLayoutGetPadding(node_ref, YGEdge.Left)
    padding_right = YGNodeLayoutGetPadding(node_ref, YGEdge.Right)
    
    # Get computed border (left and right)
    border_left = YGNodeLayoutGetBorder(node_ref, YGEdge.Left)
    border_right = YGNodeLayoutGetBorder(node_ref, YGEdge.Right)
    
    return width - padding_left - padding_right - border_left - border_right

