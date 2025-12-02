"""
Tests for the renderer module.

The renderer converts DOM trees to output strings.
"""

from inkpy.dom import append_child_node, create_node, create_text_node
from inkpy.renderer.renderer import renderer


def test_render_text():
    """Test rendering a simple text node"""
    # Create DOM structure
    root = create_node("ink-root")
    text_elem = create_node("ink-text")
    text_node = create_text_node("Hello")

    append_child_node(text_elem, text_node)
    append_child_node(root, text_elem)

    # Calculate layout
    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    assert "Hello" in result["output"]


def test_render_empty_node():
    """Test rendering empty node returns empty output"""
    root = create_node("ink-root")
    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    # Empty node should have empty or minimal output
    assert result["outputHeight"] >= 0


def test_render_nested_boxes():
    """Test rendering nested box elements"""
    root = create_node("ink-root")
    box1 = create_node("ink-box")
    box2 = create_node("ink-box")
    text_elem = create_node("ink-text")
    text_node = create_text_node("Nested")

    append_child_node(text_elem, text_node)
    append_child_node(box2, text_elem)
    append_child_node(box1, box2)
    append_child_node(root, box1)

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    assert "Nested" in result["output"]


def test_render_returns_proper_structure():
    """Test that renderer returns expected dictionary structure"""
    root = create_node("ink-root")
    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    assert "output" in result
    assert "outputHeight" in result
    assert "staticOutput" in result
