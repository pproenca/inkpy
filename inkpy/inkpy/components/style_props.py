"""
Style prop mapping utilities.

Provides snake_case to camelCase conversion for style props.
"""

from typing import Any

# Style prop name mapping (snake_case -> camelCase)
STYLE_PROP_MAP = {
    "flex_direction": "flexDirection",
    "align_items": "alignItems",
    "align_content": "alignContent",
    "align_self": "alignSelf",
    "justify_content": "justifyContent",
    "flex_wrap": "flexWrap",
    "flex_grow": "flexGrow",
    "flex_shrink": "flexShrink",
    "flex_basis": "flexBasis",
    "padding_top": "paddingTop",
    "padding_bottom": "paddingBottom",
    "padding_left": "paddingLeft",
    "padding_right": "paddingRight",
    "margin_top": "marginTop",
    "margin_bottom": "marginBottom",
    "margin_left": "marginLeft",
    "margin_right": "marginRight",
    "border_style": "borderStyle",
    "border_color": "borderColor",
    "background_color": "backgroundColor",
    "min_width": "minWidth",
    "min_height": "minHeight",
    "max_width": "maxWidth",
    "max_height": "maxHeight",
    "overflow_x": "overflowX",
    "overflow_y": "overflowY",
    "text_wrap": "textWrap",
}

# Single-word style props that don't need conversion but should be treated as styles
SINGLE_WORD_STYLE_PROPS = {
    "padding",
    "margin",
    "width",
    "height",
    "flex",
    "gap",
    "overflow",
    "display",
    "position",
}


def normalize_style_props(kwargs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Separate and normalize style props from other kwargs.

    Converts snake_case style props to camelCase.

    Args:
        kwargs: Dictionary of keyword arguments

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
            # Already camelCase, pass through as style
            style_props[key] = value
        elif key in SINGLE_WORD_STYLE_PROPS:
            # Single-word style props, pass through as style
            style_props[key] = value
        else:
            # Not a style prop
            other_kwargs[key] = value

    return style_props, other_kwargs
