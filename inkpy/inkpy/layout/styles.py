"""
Style application module for Yoga nodes.

Ports the style system from Ink's styles.ts to Python, applying
CSS-like styles to Yoga layout nodes.
"""

import contextlib
from typing import Any

import poga

from .yoga_node import YogaNode


def apply_styles(node: YogaNode, style: dict[str, Any]) -> None:
    """
    Apply style properties to a Yoga node.

    This function processes all style properties and applies them
    to the node's layout configuration.

    Args:
        node: The YogaNode to apply styles to
        style: Dictionary of style properties
    """
    layout = node.view.poga_layout()

    # Apply styles in order: position, margin, padding, flex, dimensions, display, border, gap
    _apply_position_styles(layout, style)
    _apply_margin_styles(layout, style)
    _apply_padding_styles(layout, style)
    _apply_flex_styles(layout, style)
    _apply_dimension_styles(layout, style)
    _apply_display_styles(layout, style)
    _apply_border_styles(layout, style)
    _apply_gap_styles(layout, style)


def _apply_position_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply position styles (absolute/relative)."""
    if "position" in style:
        if style["position"] == "absolute":
            layout.position_type = poga.YGPositionType.Absolute
        elif style["position"] == "relative":
            layout.position_type = poga.YGPositionType.Relative


def _apply_margin_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply margin styles."""
    if "margin" in style:
        value = style.get("margin", 0)
        layout.margin = poga.YGValue(value, poga.YGUnit.Point)

    if "marginX" in style:
        value = style.get("marginX", 0)
        layout.margin_horizontal = poga.YGValue(value, poga.YGUnit.Point)

    if "marginY" in style:
        value = style.get("marginY", 0)
        layout.margin_vertical = poga.YGValue(value, poga.YGUnit.Point)

    if "marginLeft" in style:
        value = style.get("marginLeft", 0)
        layout.margin_left = poga.YGValue(value, poga.YGUnit.Point)

    if "marginRight" in style:
        value = style.get("marginRight", 0)
        layout.margin_right = poga.YGValue(value, poga.YGUnit.Point)

    if "marginTop" in style:
        value = style.get("marginTop", 0)
        layout.margin_top = poga.YGValue(value, poga.YGUnit.Point)

    if "marginBottom" in style:
        value = style.get("marginBottom", 0)
        layout.margin_bottom = poga.YGValue(value, poga.YGUnit.Point)


def _apply_padding_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply padding styles."""
    if "padding" in style:
        value = style.get("padding", 0)
        layout.padding = poga.YGValue(value, poga.YGUnit.Point)

    if "paddingX" in style:
        value = style.get("paddingX", 0)
        layout.padding_horizontal = poga.YGValue(value, poga.YGUnit.Point)

    if "paddingY" in style:
        value = style.get("paddingY", 0)
        layout.padding_vertical = poga.YGValue(value, poga.YGUnit.Point)

    if "paddingLeft" in style:
        value = style.get("paddingLeft", 0)
        layout.padding_left = poga.YGValue(value, poga.YGUnit.Point)

    if "paddingRight" in style:
        value = style.get("paddingRight", 0)
        layout.padding_right = poga.YGValue(value, poga.YGUnit.Point)

    if "paddingTop" in style:
        value = style.get("paddingTop", 0)
        layout.padding_top = poga.YGValue(value, poga.YGUnit.Point)

    if "paddingBottom" in style:
        value = style.get("paddingBottom", 0)
        layout.padding_bottom = poga.YGValue(value, poga.YGUnit.Point)


def _apply_flex_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply flex-related styles."""
    if "flexGrow" in style:
        layout.flex_grow = style.get("flexGrow", 0)

    if "flexShrink" in style:
        value = style.get("flexShrink")
        if isinstance(value, (int, float)):
            layout.flex_shrink = value
        else:
            layout.flex_shrink = 1

    if "flexWrap" in style:
        wrap = style.get("flexWrap")
        if wrap == "nowrap":
            layout.flex_wrap = poga.YGWrap.NoWrap
        elif wrap == "wrap":
            layout.flex_wrap = poga.YGWrap.Wrap
        elif wrap == "wrap-reverse":
            layout.flex_wrap = poga.YGWrap.WrapReverse

    if "flexDirection" in style:
        direction = style.get("flexDirection")
        if direction == "row":
            layout.flex_direction = poga.YGFlexDirection.Row
        elif direction == "row-reverse":
            layout.flex_direction = poga.YGFlexDirection.RowReverse
        elif direction == "column":
            layout.flex_direction = poga.YGFlexDirection.Column
        elif direction == "column-reverse":
            layout.flex_direction = poga.YGFlexDirection.ColumnReverse

    if "flexBasis" in style:
        basis = style.get("flexBasis")
        if isinstance(basis, (int, float)):
            layout.flex_basis = poga.YGValue(basis, poga.YGUnit.Point)
        elif isinstance(basis, str) and basis.endswith("%"):
            # Parse percentage
            percent_value = int(basis.rstrip("%"))
            layout.flex_basis = poga.YGValue(percent_value, poga.YGUnit.Percent)
        else:
            # Auto/undefined
            layout.flex_basis = poga.YGValue(poga.YGUndefined, poga.YGUnit.Undefined)

    if "alignItems" in style:
        align = style.get("alignItems")
        if align == "stretch" or not align:
            layout.align_items = poga.YGAlign.Stretch
        elif align == "flex-start":
            layout.align_items = poga.YGAlign.FlexStart
        elif align == "center":
            layout.align_items = poga.YGAlign.Center
        elif align == "flex-end":
            layout.align_items = poga.YGAlign.FlexEnd

    if "alignSelf" in style:
        align = style.get("alignSelf")
        if align == "auto" or not align:
            layout.align_self = poga.YGAlign.Auto
        elif align == "flex-start":
            layout.align_self = poga.YGAlign.FlexStart
        elif align == "center":
            layout.align_self = poga.YGAlign.Center
        elif align == "flex-end":
            layout.align_self = poga.YGAlign.FlexEnd
        elif align == "stretch":
            layout.align_self = poga.YGAlign.Stretch

    if "justifyContent" in style:
        justify = style.get("justifyContent")
        if justify == "flex-start" or not justify:
            layout.justify_content = poga.YGJustify.FlexStart
        elif justify == "center":
            layout.justify_content = poga.YGJustify.Center
        elif justify == "flex-end":
            layout.justify_content = poga.YGJustify.FlexEnd
        elif justify == "space-between":
            layout.justify_content = poga.YGJustify.SpaceBetween
        elif justify == "space-around":
            layout.justify_content = poga.YGJustify.SpaceAround
        elif justify == "space-evenly":
            layout.justify_content = poga.YGJustify.SpaceEvenly


def _apply_dimension_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply width, height, minWidth, minHeight styles."""
    if "width" in style:
        width = style.get("width")
        if isinstance(width, (int, float)):
            layout.width = poga.YGValue(width, poga.YGUnit.Point)
        elif isinstance(width, str) and width.endswith("%"):
            percent_value = int(width.rstrip("%"))
            layout.width = poga.YGValue(percent_value, poga.YGUnit.Percent)
        else:
            layout.width = poga.YGValue(poga.YGUndefined, poga.YGUnit.Undefined)

    if "height" in style:
        height = style.get("height")
        if isinstance(height, (int, float)):
            layout.height = poga.YGValue(height, poga.YGUnit.Point)
        elif isinstance(height, str) and height.endswith("%"):
            percent_value = int(height.rstrip("%"))
            layout.height = poga.YGValue(percent_value, poga.YGUnit.Percent)
        else:
            layout.height = poga.YGValue(poga.YGUndefined, poga.YGUnit.Undefined)

    if "minWidth" in style:
        min_width = style.get("minWidth")
        if isinstance(min_width, str) and min_width.endswith("%"):
            percent_value = int(min_width.rstrip("%"))
            layout.min_width = poga.YGValue(percent_value, poga.YGUnit.Percent)
        else:
            layout.min_width = poga.YGValue(min_width or 0, poga.YGUnit.Point)

    if "minHeight" in style:
        min_height = style.get("minHeight")
        if isinstance(min_height, str) and min_height.endswith("%"):
            percent_value = int(min_height.rstrip("%"))
            layout.min_height = poga.YGValue(percent_value, poga.YGUnit.Percent)
        else:
            layout.min_height = poga.YGValue(min_height or 0, poga.YGUnit.Point)


def _apply_display_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply display styles (flex/none)."""
    if "display" in style:
        if style.get("display") == "flex":
            layout.display = poga.YGDisplay.Flex
        elif style.get("display") == "none":
            layout.display = poga.YGDisplay.DisplayNone


def _apply_border_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply border styles."""
    if "borderStyle" in style:
        border_width = 1 if style.get("borderStyle") else 0

        if style.get("borderTop", True) is not False:
            layout.border_top_width = border_width
        else:
            layout.border_top_width = 0

        if style.get("borderBottom", True) is not False:
            layout.border_bottom_width = border_width
        else:
            layout.border_bottom_width = 0

        if style.get("borderLeft", True) is not False:
            layout.border_left_width = border_width
        else:
            layout.border_left_width = 0

        if style.get("borderRight", True) is not False:
            layout.border_right_width = border_width
        else:
            layout.border_right_width = 0


def _apply_gap_styles(layout: poga.PogaLayout, style: dict[str, Any]) -> None:
    """Apply gap styles (gap, columnGap, rowGap)."""
    if "gap" in style:
        value = style.get("gap", 0)
        # Poga doesn't have a direct 'gap' property, so we set both column and row gap
        # Check if poga has gap properties
        try:
            layout.column_gap = poga.YGValue(value, poga.YGUnit.Point)
            layout.row_gap = poga.YGValue(value, poga.YGUnit.Point)
        except AttributeError:
            # If gap properties don't exist, skip
            pass

    if "columnGap" in style:
        value = style.get("columnGap", 0)
        with contextlib.suppress(AttributeError):
            layout.column_gap = poga.YGValue(value, poga.YGUnit.Point)

    if "rowGap" in style:
        value = style.get("rowGap", 0)
        with contextlib.suppress(AttributeError):
            layout.row_gap = poga.YGValue(value, poga.YGUnit.Point)
