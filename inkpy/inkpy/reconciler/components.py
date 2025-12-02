"""
Custom Reconciler Components - Box, Text components for the custom reconciler.

These are simplified versions of the ReactPy-based components that work
with our custom reconciler for synchronous state updates.
"""

from typing import Any, Optional, Union

from inkpy.reconciler.element import Element, create_element


def _normalize_style_props(props: dict[str, Any]) -> dict[str, Any]:
    """Convert snake_case props to camelCase for style."""
    style_mapping = {
        # Layout
        "flex_direction": "flexDirection",
        "flex_wrap": "flexWrap",
        "flex_grow": "flexGrow",
        "flex_shrink": "flexShrink",
        "flex_basis": "flexBasis",
        "align_items": "alignItems",
        "align_self": "alignSelf",
        "justify_content": "justifyContent",
        # Dimensions
        "min_width": "minWidth",
        "min_height": "minHeight",
        # Spacing
        "padding_top": "paddingTop",
        "padding_bottom": "paddingBottom",
        "padding_left": "paddingLeft",
        "padding_right": "paddingRight",
        "padding_x": "paddingX",
        "padding_y": "paddingY",
        "margin_top": "marginTop",
        "margin_bottom": "marginBottom",
        "margin_left": "marginLeft",
        "margin_right": "marginRight",
        "margin_x": "marginX",
        "margin_y": "marginY",
        # Border
        "border_style": "borderStyle",
        "border_color": "borderColor",
        "border_top": "borderTop",
        "border_bottom": "borderBottom",
        "border_left": "borderLeft",
        "border_right": "borderRight",
        # Colors
        "background_color": "backgroundColor",
        # Overflow
        "overflow_x": "overflowX",
        "overflow_y": "overflowY",
        # Text
        "text_wrap": "textWrap",
    }

    result = {}
    for key, value in props.items():
        camel_key = style_mapping.get(key, key)
        result[camel_key] = value

    return result


def Box(
    *children,
    style: Optional[dict[str, Any]] = None,
    # Common style shortcuts
    padding: Optional[int] = None,
    margin: Optional[int] = None,
    width: Optional[Union[int, str]] = None,
    height: Optional[Union[int, str]] = None,
    flex_direction: Optional[str] = None,
    border_style: Optional[str] = None,
    border_color: Optional[str] = None,
    background_color: Optional[str] = None,
    # ARIA
    aria_label: Optional[str] = None,
    aria_role: Optional[str] = None,
    **kwargs,
) -> Element:
    """
    Box component - A flexbox container.

    Args:
        children: Child elements
        style: Style dictionary
        padding: Padding (shorthand for all sides)
        margin: Margin (shorthand for all sides)
        width: Width
        height: Height
        flex_direction: 'row' or 'column'
        border_style: Border style ('single', 'double', 'round', etc.)
        border_color: Border color
        background_color: Background color
        aria_label: ARIA label
        aria_role: ARIA role
        **kwargs: Additional style props (snake_case or camelCase)

    Returns:
        Element for ink-box
    """
    # Build style
    final_style = {
        "flexWrap": "nowrap",
        "flexDirection": "row",
        "flexGrow": 0,
        "flexShrink": 1,
    }

    if style:
        final_style.update(_normalize_style_props(style))

    # Apply shortcuts
    if padding is not None:
        final_style["padding"] = padding
    if margin is not None:
        final_style["margin"] = margin
    if width is not None:
        final_style["width"] = width
    if height is not None:
        final_style["height"] = height
    if flex_direction is not None:
        final_style["flexDirection"] = flex_direction
    if border_style is not None:
        final_style["borderStyle"] = border_style
    if border_color is not None:
        final_style["borderColor"] = border_color
    if background_color is not None:
        final_style["backgroundColor"] = background_color

    # Apply additional kwargs as style
    extra_style = _normalize_style_props(kwargs)
    final_style.update(extra_style)

    # Build props
    props = {"style": final_style}

    if aria_label:
        props["aria-label"] = aria_label
    if aria_role:
        props["aria-role"] = aria_role

    # Create element
    return create_element("ink-box", props, *children)


def Text(
    *children,
    color: Optional[str] = None,
    background_color: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strikethrough: bool = False,
    dim: bool = False,
    inverse: bool = False,
    wrap: Optional[str] = None,  # 'wrap', 'truncate', 'truncate-start', 'truncate-middle'
    **kwargs,
) -> Element:
    """
    Text component - Renders styled text.

    Args:
        children: Text content (strings or nested Text elements)
        color: Text color (ANSI color name or hex)
        background_color: Background color
        bold: Bold text
        italic: Italic text
        underline: Underlined text
        strikethrough: Strikethrough text
        dim: Dimmed text
        inverse: Inverted colors
        wrap: Text wrapping mode
        **kwargs: Additional style props

    Returns:
        Element for ink-text
    """
    style = {}

    if color is not None:
        style["color"] = color
    if background_color is not None:
        style["backgroundColor"] = background_color
    if bold:
        style["bold"] = True
    if italic:
        style["italic"] = True
    if underline:
        style["underline"] = True
    if strikethrough:
        style["strikethrough"] = True
    if dim:
        style["dimColor"] = True
    if inverse:
        style["inverse"] = True
    if wrap is not None:
        style["textWrap"] = wrap

    # Apply additional kwargs
    extra_style = _normalize_style_props(kwargs)
    style.update(extra_style)

    props = {"style": style} if style else {}

    return create_element("ink-text", props, *children)


def Newline(count: int = 1) -> Element:
    """
    Newline component - Adds line breaks.

    Args:
        count: Number of newlines

    Returns:
        Element for ink-text with newlines
    """
    return create_element("ink-text", {}, "\n" * count)


def Spacer() -> Element:
    """
    Spacer component - Flexible space that expands.

    Returns:
        Element that grows to fill available space
    """
    return create_element("ink-box", {"style": {"flexGrow": 1}})
