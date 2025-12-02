# tests/reconciler/test_components.py
"""Tests for custom reconciler components"""

from inkpy.reconciler.components import (
    Box,
    Newline,
    Spacer,
    Text,
    _normalize_style_props,
)


def test_box_creates_element():
    """Test Box creates ink-box element"""
    element = Box()

    assert element.type == "ink-box"
    assert "style" in element.props


def test_box_with_children():
    """Test Box with children"""
    child = Text("Hello")
    element = Box(child)

    assert element.type == "ink-box"
    assert len(element.props["children"]) == 1


def test_box_with_style_shortcuts():
    """Test Box style shortcuts"""
    element = Box(
        padding=2,
        flex_direction="column",
        border_style="single",
    )

    assert element.props["style"]["padding"] == 2
    assert element.props["style"]["flexDirection"] == "column"
    assert element.props["style"]["borderStyle"] == "single"


def test_text_creates_element():
    """Test Text creates ink-text element"""
    element = Text("Hello World")

    assert element.type == "ink-text"
    assert "Hello World" in element.props["children"]


def test_text_with_styles():
    """Test Text with color and formatting"""
    element = Text("Bold Text", color="green", bold=True)

    assert element.props["style"]["color"] == "green"
    assert element.props["style"]["bold"] is True


def test_text_nested():
    """Test nested Text elements"""
    inner = Text("inner", color="red")
    outer = Text(inner, "and outer")

    assert outer.type == "ink-text"
    assert len(outer.props["children"]) == 2


def test_newline():
    """Test Newline component"""
    element = Newline(3)

    assert element.type == "ink-text"
    assert "\n\n\n" in element.props["children"]


def test_spacer():
    """Test Spacer component"""
    element = Spacer()

    assert element.type == "ink-box"
    assert element.props["style"]["flexGrow"] == 1


# === Tests for _normalize_style_props ===


def test_normalize_style_props_layout():
    """Test normalization of layout props"""
    props = {
        "flex_direction": "column",
        "flex_wrap": "wrap",
        "flex_grow": 1,
        "flex_shrink": 0,
        "align_items": "center",
        "justify_content": "space-between",
    }
    result = _normalize_style_props(props)

    assert result["flexDirection"] == "column"
    assert result["flexWrap"] == "wrap"
    assert result["flexGrow"] == 1
    assert result["flexShrink"] == 0
    assert result["alignItems"] == "center"
    assert result["justifyContent"] == "space-between"


def test_normalize_style_props_spacing():
    """Test normalization of spacing props"""
    props = {
        "padding_top": 1,
        "padding_bottom": 2,
        "padding_left": 3,
        "padding_right": 4,
        "margin_top": 5,
        "margin_bottom": 6,
    }
    result = _normalize_style_props(props)

    assert result["paddingTop"] == 1
    assert result["paddingBottom"] == 2
    assert result["paddingLeft"] == 3
    assert result["paddingRight"] == 4
    assert result["marginTop"] == 5
    assert result["marginBottom"] == 6


def test_normalize_style_props_border():
    """Test normalization of border props"""
    props = {
        "border_style": "single",
        "border_color": "red",
        "border_top": True,
        "border_bottom": True,
    }
    result = _normalize_style_props(props)

    assert result["borderStyle"] == "single"
    assert result["borderColor"] == "red"
    assert result["borderTop"] is True
    assert result["borderBottom"] is True


def test_normalize_style_props_already_camel():
    """Test props already in camelCase pass through"""
    props = {
        "flexDirection": "row",
        "backgroundColor": "blue",
    }
    result = _normalize_style_props(props)

    assert result["flexDirection"] == "row"
    assert result["backgroundColor"] == "blue"


# === Tests for Box shortcuts ===


def test_box_margin_shortcut():
    """Test Box margin shortcut"""
    element = Box(margin=3)
    assert element.props["style"]["margin"] == 3


def test_box_width_shortcut():
    """Test Box width shortcut"""
    element = Box(width=50)
    assert element.props["style"]["width"] == 50


def test_box_height_shortcut():
    """Test Box height shortcut"""
    element = Box(height=10)
    assert element.props["style"]["height"] == 10


def test_box_border_color_shortcut():
    """Test Box border_color shortcut"""
    element = Box(border_color="blue")
    assert element.props["style"]["borderColor"] == "blue"


def test_box_background_color_shortcut():
    """Test Box background_color shortcut"""
    element = Box(background_color="yellow")
    assert element.props["style"]["backgroundColor"] == "yellow"


def test_box_aria_label():
    """Test Box aria_label prop"""
    element = Box(aria_label="Navigation menu")
    assert element.props["aria-label"] == "Navigation menu"


def test_box_aria_role():
    """Test Box aria_role prop"""
    element = Box(aria_role="navigation")
    assert element.props["aria-role"] == "navigation"


def test_box_with_style_dict():
    """Test Box with explicit style dict"""
    element = Box(style={"flex_direction": "column", "gap": 2})
    assert element.props["style"]["flexDirection"] == "column"
    assert element.props["style"]["gap"] == 2


def test_box_kwargs_override_style():
    """Test Box kwargs override style dict"""
    element = Box(style={"padding": 1}, padding=5)
    assert element.props["style"]["padding"] == 5


# === Tests for Text styles ===


def test_text_background_color():
    """Test Text background_color prop"""
    element = Text("test", background_color="red")
    assert element.props["style"]["backgroundColor"] == "red"


def test_text_italic():
    """Test Text italic prop"""
    element = Text("test", italic=True)
    assert element.props["style"]["italic"] is True


def test_text_underline():
    """Test Text underline prop"""
    element = Text("test", underline=True)
    assert element.props["style"]["underline"] is True


def test_text_strikethrough():
    """Test Text strikethrough prop"""
    element = Text("test", strikethrough=True)
    assert element.props["style"]["strikethrough"] is True


def test_text_dim():
    """Test Text dim prop"""
    element = Text("test", dim=True)
    assert element.props["style"]["dimColor"] is True


def test_text_inverse():
    """Test Text inverse prop"""
    element = Text("test", inverse=True)
    assert element.props["style"]["inverse"] is True


def test_text_wrap():
    """Test Text wrap prop"""
    element = Text("test", wrap="truncate")
    assert element.props["style"]["textWrap"] == "truncate"


def test_text_no_style():
    """Test Text with no style props has empty or no style"""
    element = Text("plain text")
    # Should have empty style or no style key
    assert element.props.get("style", {}) == {}


def test_text_kwargs_as_style():
    """Test Text accepts kwargs as style props"""
    element = Text("test", flex_grow=1, padding_left=2)
    assert element.props["style"]["flexGrow"] == 1
    assert element.props["style"]["paddingLeft"] == 2


# === Test Newline default ===


def test_newline_default():
    """Test Newline with default count=1"""
    element = Newline()
    assert element.type == "ink-text"
    assert "\n" in element.props["children"]
