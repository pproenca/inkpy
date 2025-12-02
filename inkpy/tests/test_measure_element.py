"""
Tests for measure_element module - Get computed dimensions of DOM elements.

Ported from: src/measure-element.ts
"""

from inkpy.dom import create_node
from inkpy.layout.styles import apply_styles
from inkpy.measure_element import measure_element


def test_measure_element_basic():
    """Test measuring element dimensions"""
    node = create_node("ink-box")
    apply_styles(node.yoga_node, {"width": 50, "height": 10})
    node.yoga_node.calculate_layout(width=50)

    result = measure_element(node)

    assert result["width"] == 50
    assert result["height"] == 10


def test_measure_element_no_yoga():
    """Test measuring element without yoga node"""
    node = create_node("ink-virtual-text")  # No yoga node
    result = measure_element(node)

    assert result["width"] == 0
    assert result["height"] == 0


def test_measure_element_uses_computed_dimensions():
    """Test that measure_element uses computed dimensions (matches TypeScript API)"""
    node = create_node("ink-box")
    apply_styles(node.yoga_node, {"width": 100, "height": 50})
    node.yoga_node.calculate_layout(width=100, height=50)

    result = measure_element(node)

    # Should match get_computed_width/height
    assert result["width"] == int(node.yoga_node.get_computed_width())
    assert result["height"] == int(node.yoga_node.get_computed_height())


def test_measure_element_returns_zero_before_layout():
    """Test that measure_element returns zero before layout calculation"""
    node = create_node("ink-box")
    apply_styles(node.yoga_node, {"width": 100, "height": 50})
    # Don't call calculate_layout

    result = measure_element(node)

    # Should return zero before layout is calculated
    assert result["width"] == 0
    assert result["height"] == 0
