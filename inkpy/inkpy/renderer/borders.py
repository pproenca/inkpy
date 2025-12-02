"""
Border rendering module.

Ports border rendering functionality from Ink's render-border.ts.
Supports various border styles: single, double, round, bold, etc.
"""

from typing import Optional, Union

from .colorize import colorize
from .output import Output

# Border character sets (ported from cli-boxes)
BORDER_STYLES: dict[str, dict[str, str]] = {
    "single": {
        "topLeft": "┌",
        "topRight": "┐",
        "bottomLeft": "└",
        "bottomRight": "┘",
        "top": "─",
        "bottom": "─",
        "left": "│",
        "right": "│",
        "horizontal": "─",
        "vertical": "│",
    },
    "double": {
        "topLeft": "╔",
        "topRight": "╗",
        "bottomLeft": "╚",
        "bottomRight": "╝",
        "top": "═",
        "bottom": "═",
        "left": "║",
        "right": "║",
        "horizontal": "═",
        "vertical": "║",
    },
    "round": {
        "topLeft": "╭",
        "topRight": "╮",
        "bottomLeft": "╰",
        "bottomRight": "╯",
        "top": "─",
        "bottom": "─",
        "left": "│",
        "right": "│",
        "horizontal": "─",
        "vertical": "│",
    },
    "bold": {
        "topLeft": "┏",
        "topRight": "┓",
        "bottomLeft": "┗",
        "bottomRight": "┛",
        "top": "━",
        "bottom": "━",
        "left": "┃",
        "right": "┃",
        "horizontal": "━",
        "vertical": "┃",
    },
    "singleDouble": {
        "topLeft": "╓",
        "topRight": "╖",
        "bottomLeft": "╙",
        "bottomRight": "╜",
        "top": "─",
        "bottom": "─",
        "left": "║",
        "right": "║",
        "horizontal": "─",
        "vertical": "║",
    },
    "doubleSingle": {
        "topLeft": "╒",
        "topRight": "╕",
        "bottomLeft": "╘",
        "bottomRight": "╛",
        "top": "═",
        "bottom": "═",
        "left": "│",
        "right": "│",
        "horizontal": "═",
        "vertical": "│",
    },
    "classic": {
        "topLeft": "+",
        "topRight": "+",
        "bottomLeft": "+",
        "bottomRight": "+",
        "top": "-",
        "bottom": "-",
        "left": "|",
        "right": "|",
        "horizontal": "-",
        "vertical": "|",
    },
}


def get_border_chars(style: Union[str, dict[str, str]]) -> dict[str, str]:
    """
    Get border character set for a given style.

    Args:
        style: Border style name (e.g., 'single', 'double') or custom border dict

    Returns:
        Dictionary with border characters
    """
    if isinstance(style, dict):
        return style

    return BORDER_STYLES.get(style, BORDER_STYLES["single"])


def _apply_dim(text: str) -> str:
    """
    Apply dim effect to text (reduces brightness).

    Args:
        text: Text to dim

    Returns:
        Dimmed text with ANSI codes
    """
    # ANSI dim code is \x1b[2m
    return f"\x1b[2m{text}\x1b[0m"


def render_border(
    output: Output,
    x: int,
    y: int,
    width: int,
    height: int,
    style: Union[str, dict[str, str]] = "single",
    borderTop: Optional[bool] = True,
    borderBottom: Optional[bool] = True,
    borderLeft: Optional[bool] = True,
    borderRight: Optional[bool] = True,
    borderColor: Optional[Union[str, int]] = None,
    borderTopColor: Optional[Union[str, int]] = None,
    borderBottomColor: Optional[Union[str, int]] = None,
    borderLeftColor: Optional[Union[str, int]] = None,
    borderRightColor: Optional[Union[str, int]] = None,
    borderDimColor: Optional[bool] = None,
    borderTopDimColor: Optional[bool] = None,
    borderBottomDimColor: Optional[bool] = None,
    borderLeftDimColor: Optional[bool] = None,
    borderRightDimColor: Optional[bool] = None,
) -> None:
    """
    Render a border around a rectangular area.

    Args:
        output: Output buffer to write to
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of the box (including borders)
        height: Height of the box (including borders)
        style: Border style name or custom border character dict
        borderTop: Whether to show top border (default: True)
        borderBottom: Whether to show bottom border (default: True)
        borderLeft: Whether to show left border (default: True)
        borderRight: Whether to show right border (default: True)
        borderColor: Color for all borders
        borderTopColor: Color for top border (overrides borderColor)
        borderBottomColor: Color for bottom border (overrides borderColor)
        borderLeftColor: Color for left border (overrides borderColor)
        borderRightColor: Color for right border (overrides borderColor)
        borderDimColor: Whether to dim all borders
        borderTopDimColor: Whether to dim top border
        borderBottomDimColor: Whether to dim bottom border
        borderLeftDimColor: Whether to dim left border
        borderRightDimColor: Whether to dim right border
    """
    box = get_border_chars(style)

    # Determine which borders to show
    show_top = borderTop is not False
    show_bottom = borderBottom is not False
    show_left = borderLeft is not False
    show_right = borderRight is not False

    # Calculate content width (excluding borders)
    content_width = width
    if show_left:
        content_width -= 1
    if show_right:
        content_width -= 1

    # Determine border colors
    top_color = borderTopColor if borderTopColor is not None else borderColor
    bottom_color = borderBottomColor if borderBottomColor is not None else borderColor
    left_color = borderLeftColor if borderLeftColor is not None else borderColor
    right_color = borderRightColor if borderRightColor is not None else borderColor

    # Determine dim settings
    dim_top = borderTopDimColor if borderTopDimColor is not None else borderDimColor
    dim_bottom = borderBottomDimColor if borderBottomDimColor is not None else borderDimColor
    dim_left = borderLeftDimColor if borderLeftDimColor is not None else borderDimColor
    dim_right = borderRightDimColor if borderRightDimColor is not None else borderDimColor

    # Render top border
    if show_top:
        top_border = ""
        if show_left:
            top_border += box["topLeft"]
        top_border += box["top"] * content_width
        if show_right:
            top_border += box["topRight"]

        top_border = colorize(top_border, top_color, "foreground")
        if dim_top:
            top_border = _apply_dim(top_border)

        output.write(x, y, top_border, transformers=[])

    # Calculate vertical border height
    vertical_height = height
    if show_top:
        vertical_height -= 1
    if show_bottom:
        vertical_height -= 1

    # Render left border
    if show_left and vertical_height > 0:
        left_char = colorize(box["left"], left_color, "foreground")
        if dim_left:
            left_char = _apply_dim(left_char)

        left_border = (left_char + "\n") * vertical_height
        offset_y = 1 if show_top else 0
        output.write(x, y + offset_y, left_border, transformers=[])

    # Render right border
    if show_right and vertical_height > 0:
        right_char = colorize(box["right"], right_color, "foreground")
        if dim_right:
            right_char = _apply_dim(right_char)

        right_border = (right_char + "\n") * vertical_height
        offset_y = 1 if show_top else 0
        output.write(x + width - 1, y + offset_y, right_border, transformers=[])

    # Render bottom border
    if show_bottom:
        bottom_border = ""
        if show_left:
            bottom_border += box["bottomLeft"]
        bottom_border += box["bottom"] * content_width
        if show_right:
            bottom_border += box["bottomRight"]

        bottom_border = colorize(bottom_border, bottom_color, "foreground")
        if dim_bottom:
            bottom_border = _apply_dim(bottom_border)

        output.write(x, y + height - 1, bottom_border, transformers=[])
