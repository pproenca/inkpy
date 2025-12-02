"""
Tests for get_max_width module - Calculate maximum content width.

Ported from: src/get-max-width.ts
"""

from inkpy.get_max_width import get_max_width
from inkpy.layout.styles import apply_styles
from inkpy.layout.yoga_node import YogaNode


def test_get_max_width_simple():
    """Test max width without padding/border"""
    node = YogaNode()
    apply_styles(node, {"width": 100})
    node.calculate_layout(width=100)
    assert get_max_width(node) == 100


def test_get_max_width_with_padding():
    """Test max width with padding"""
    node = YogaNode()
    apply_styles(node, {"width": 100, "paddingLeft": 10, "paddingRight": 10})
    node.calculate_layout(width=100)
    assert get_max_width(node) == 80  # 100 - 10 - 10


def test_get_max_width_with_border():
    """Test max width with border"""
    node = YogaNode()
    apply_styles(
        node, {"width": 100, "borderStyle": "single", "borderLeft": True, "borderRight": True}
    )
    node.calculate_layout(width=100)
    assert get_max_width(node) == 98  # 100 - 1 - 1


def test_get_max_width_with_padding_and_border():
    """Test max width with both padding and border"""
    node = YogaNode()
    apply_styles(
        node,
        {
            "width": 100,
            "paddingLeft": 5,
            "paddingRight": 5,
            "borderStyle": "single",
            "borderLeft": True,
            "borderRight": True,
        },
    )
    node.calculate_layout(width=100)
    assert get_max_width(node) == 88  # 100 - 5 - 5 - 1 - 1
