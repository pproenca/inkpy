"""
Text component module.

Enhanced Text component with full styling support and inherited background.
"""
from typing import Optional, Union, Any
from reactpy import component, html
from reactpy.core.hooks import use_context
from ..renderer.colorize import colorize
from .background_context import background_context
from .accessibility_context import accessibility_context


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
    aria_label: Optional[str] = None,
    aria_hidden: bool = False,
    **kwargs
):
    """
    Text component with full styling support and inherited background.
    
    Args:
        children: Text content
        color: Foreground color
        backgroundColor: Background color (explicit, overrides inherited)
        dimColor: Dim the color
        bold: Make text bold
        italic: Make text italic
        underline: Underline text
        strikethrough: Strikethrough text
        inverse: Inverse colors
        wrap: Text wrap mode ('wrap', 'truncate-end', 'truncate-middle', 'truncate-start')
        style: Additional style dictionary
        aria_label: Label for screen readers
        aria_hidden: Hide element from screen readers
        **kwargs: Additional props
    """
    # Get accessibility context
    try:
        accessibility_ctx = use_context(accessibility_context)
        is_screen_reader_enabled = accessibility_ctx.get('is_screen_reader_enabled', False)
    except RuntimeError:
        # Context not available (e.g., in tests without Layout)
        is_screen_reader_enabled = False
    
    # Get inherited background color from context
    try:
        inherited_background = use_context(background_context)
    except RuntimeError:
        # Context not available (e.g., in tests without Layout)
        inherited_background = None
    
    # Use explicit backgroundColor if provided, otherwise use inherited
    effective_background = backgroundColor if backgroundColor is not None else inherited_background
    
    # Handle screen reader mode
    # If screen reader enabled and aria-hidden, return None
    if is_screen_reader_enabled and aria_hidden:
        return None
    
    # Determine children: use aria-label if screen reader enabled and aria-label provided
    children_or_aria_label = (
        aria_label if (is_screen_reader_enabled and aria_label) else children
    )
    
    # Return None if no content
    if children_or_aria_label is None:
        return None
    
    if style is None:
        style = {}
    
    # Create transform function for text styling
    def transform(text: str, index: int) -> str:
        return _apply_text_styles(
            text,
            color=color,
            backgroundColor=effective_background,
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
    # Use children_or_aria_label for rendering
    return html.span({
        "style": final_style,
        "children": children_or_aria_label,
        "internal_transform": transform,
        **kwargs
    })
