"""
Text component module.

Enhanced Text component with full styling support.
"""
from typing import Optional, Union, Any
from reactpy import component, html
from ..renderer.colorize import colorize


def _apply_text_styles(
    text: str,
    color: Optional[Union[str, int]] = None,
    backgroundColor: Optional[Union[str, int]] = None,
    dimColor: bool = False,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strikethrough: bool = False,
    inverse: bool = False,
) -> str:
    """
    Apply text styling transformations.
    
    Args:
        text: Text to style
        color: Foreground color
        backgroundColor: Background color
        dimColor: Dim the color
        bold: Make text bold
        italic: Make text italic
        underline: Underline text
        strikethrough: Strikethrough text
        inverse: Inverse colors
    
    Returns:
        Styled text with ANSI codes
    """
    result = text
    
    # Apply dim first (affects all colors)
    if dimColor:
        result = f'\x1b[2m{result}\x1b[0m'
    
    # Apply foreground color
    if color:
        result = colorize(result, color, 'foreground')
    
    # Apply background color
    if backgroundColor:
        result = colorize(result, backgroundColor, 'background')
    
    # Apply text styles
    if bold:
        result = f'\x1b[1m{result}\x1b[0m'  # Bold
    
    if italic:
        result = f'\x1b[3m{result}\x1b[0m'  # Italic
    
    if underline:
        result = f'\x1b[4m{result}\x1b[0m'  # Underline
    
    if strikethrough:
        result = f'\x1b[9m{result}\x1b[0m'  # Strikethrough
    
    if inverse:
        result = f'\x1b[7m{result}\x1b[0m'  # Inverse
    
    return result


@component
def Text(
    children=None,
    color: Optional[Union[str, int]] = None,
    backgroundColor: Optional[Union[str, int]] = None,
    dimColor: bool = False,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strikethrough: bool = False,
    inverse: bool = False,
    wrap: str = 'wrap',
    style: Optional[dict] = None,
    **kwargs
):
    """
    Text component with full styling support.
    
    Args:
        children: Text content
        color: Foreground color
        backgroundColor: Background color
        dimColor: Dim the color
        bold: Make text bold
        italic: Make text italic
        underline: Underline text
        strikethrough: Strikethrough text
        inverse: Inverse colors
        wrap: Text wrap mode ('wrap', 'truncate-end', 'truncate-middle', 'truncate-start')
        style: Additional style dictionary
        **kwargs: Additional props
    """
    if style is None:
        style = {}
    
    # Create transform function for text styling
    def transform(text: str, index: int) -> str:
        return _apply_text_styles(
            text,
            color=color,
            backgroundColor=backgroundColor,
            dimColor=dimColor,
            bold=bold,
            italic=italic,
            underline=underline,
            strikethrough=strikethrough,
            inverse=inverse,
        )
    
    # Merge style with defaults
    final_style = {
        'flexGrow': 0,
        'flexShrink': 1,
        'flexDirection': 'row',
        'textWrap': wrap,
        **style
    }
    
    # Store transform in internal_transform (will be used by renderer)
    return html.span({
        "style": final_style,
        "children": children,
        "internal_transform": transform,
        **kwargs
    })
