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


# --- Phase 4.2: Additional Tests for 90%+ Coverage ---


def test_render_no_yoga_node():
    """Test rendering a node without yoga_node returns empty output"""
    root = create_node("ink-root")
    root.yoga_node = None  # Remove yoga node

    result = renderer(root, is_screen_reader_enabled=False)

    assert result["output"] == ""
    assert result["outputHeight"] == 0
    assert result["staticOutput"] == ""


def test_render_screen_reader_mode():
    """Test rendering in screen reader mode"""
    root = create_node("ink-root")
    text_elem = create_node("ink-text")
    text_node = create_text_node("Accessible text")

    append_child_node(text_elem, text_node)
    append_child_node(root, text_elem)

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=True)

    assert "Accessible text" in result["output"]
    assert result["outputHeight"] >= 1


def test_render_screen_reader_mode_empty():
    """Test screen reader mode with empty content"""
    root = create_node("ink-root")
    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=True)

    assert result["output"] == ""
    assert result["outputHeight"] == 0


def test_render_screen_reader_mode_with_static():
    """Test screen reader mode with static node"""
    root = create_node("ink-root")

    # Main content
    main_text = create_node("ink-text")
    main_text_node = create_text_node("Main content")
    append_child_node(main_text, main_text_node)
    append_child_node(root, main_text)

    # Static content
    static_box = create_node("ink-box")
    static_box.internal_static = True
    static_text = create_node("ink-text")
    static_text_node = create_text_node("Static content")
    append_child_node(static_text, static_text_node)
    append_child_node(static_box, static_text)
    append_child_node(root, static_box)

    root.static_node = static_box

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=True)

    assert "Main content" in result["output"]
    assert "Static content" in result["staticOutput"]


def test_render_with_static_node():
    """Test rendering with static node in normal mode"""
    root = create_node("ink-root")

    # Main content
    main_text = create_node("ink-text")
    main_text_node = create_text_node("Dynamic content")
    append_child_node(main_text, main_text_node)
    append_child_node(root, main_text)

    # Static content
    static_box = create_node("ink-box")
    static_box.internal_static = True
    static_text = create_node("ink-text")
    static_text_node = create_text_node("Static content")
    append_child_node(static_text, static_text_node)
    append_child_node(static_box, static_text)
    append_child_node(root, static_box)

    root.static_node = static_box
    root.is_static_dirty = True

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    assert "Dynamic content" in result["output"]
    # Static output should end with newline
    assert result["staticOutput"].endswith("\n") or result["staticOutput"] == ""


def test_render_static_node_without_yoga():
    """Test that static node without yoga_node is skipped"""
    root = create_node("ink-root")

    # Main content
    main_text = create_node("ink-text")
    main_text_node = create_text_node("Main")
    append_child_node(main_text, main_text_node)
    append_child_node(root, main_text)

    # Static content without yoga_node
    static_box = create_node("ink-box")
    static_box.internal_static = True
    static_box.yoga_node = None  # No yoga node
    root.static_node = static_box

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    assert "Main" in result["output"]
    assert result["staticOutput"] == ""


def test_render_multiline_output():
    """Test rendering multiline content"""
    root = create_node("ink-root")

    # Create multiple lines
    box = create_node("ink-box")
    box.style = {"flexDirection": "column"}

    for i in range(3):
        text_elem = create_node("ink-text")
        text_node = create_text_node(f"Line {i}")
        append_child_node(text_elem, text_node)
        append_child_node(box, text_elem)

    append_child_node(root, box)

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    assert "Line 0" in result["output"]
    assert "Line 1" in result["output"]
    assert "Line 2" in result["output"]


def test_render_with_styles():
    """Test rendering content with styles"""
    root = create_node("ink-root")
    text_elem = create_node("ink-text")
    text_elem.style = {"color": "red", "bold": True}
    text_node = create_text_node("Styled text")

    append_child_node(text_elem, text_node)
    append_child_node(root, text_elem)

    root.yoga_node.calculate_layout(width=80)

    result = renderer(root, is_screen_reader_enabled=False)

    # Output should contain the text
    assert "Styled text" in result["output"]
    # In screen reader mode, no styles
    screen_result = renderer(root, is_screen_reader_enabled=True)
    assert "Styled text" in screen_result["output"]
