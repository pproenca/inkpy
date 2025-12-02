"""
Background rendering module.

Ports background rendering functionality from Ink's render-background.ts.
Fills rectangular regions with background colors.
"""
from typing import Optional, Union
from .output import Output
from .colorize import colorize


def render_background(
    output: Output,
    x: int,
    y: int,
    width: int,
    height: int,
    color: Optional[Union[str, int]] = None,
    borderLeft: bool = False,
    borderRight: bool = False,
    borderTop: bool = False,
    borderBottom: bool = False,
) -> None:
    """
    Render background color in a rectangular area.
    
    Args:
        output: Output buffer to write to
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of the area (including borders if applicable)
        height: Height of the area (including borders if applicable)
        color: Background color (named color, hex, or 256-color index)
        borderLeft: Whether left border exists (adjusts content area)
        borderRight: Whether right border exists (adjusts content area)
        borderTop: Whether top border exists (adjusts content area)
        borderBottom: Whether bottom border exists (adjusts content area)
    """
    if not color:
        return
    
    if width <= 0 or height <= 0:
        return
    
    # Calculate content area accounting for borders
    left_border_width = 1 if borderLeft else 0
    right_border_width = 1 if borderRight else 0
    top_border_height = 1 if borderTop else 0
    bottom_border_height = 1 if borderBottom else 0
    
    content_width = width - left_border_width - right_border_width
    content_height = height - top_border_height - bottom_border_height
    
    if content_width <= 0 or content_height <= 0:
        return
    
    # Create background fill line (spaces with background color)
    background_line = colorize(' ' * content_width, color, 'background')
    
    # Fill each row of the content area
    for row in range(content_height):
        output.write(
            x + left_border_width,
            y + top_border_height + row,
            background_line,
            transformers=[]
        )

