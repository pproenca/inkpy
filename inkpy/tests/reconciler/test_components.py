# tests/reconciler/test_components.py
"""Tests for custom reconciler components"""

from inkpy.reconciler.components import Box, Newline, Spacer, Text


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
    assert element.props["style"]["bold"] == True


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
