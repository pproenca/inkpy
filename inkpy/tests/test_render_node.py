from inkpy.layout.text_node import TextNode
from inkpy.layout.yoga_node import YogaNode
from inkpy.renderer.output import Output
from inkpy.renderer.render_node import render_node_to_output


def test_render_text_node():
    """Test rendering a simple text node"""
    root = YogaNode()
    root.set_style({"width": 80, "height": 24})

    text_node = TextNode("Hello")
    root.add_child(text_node)

    root.calculate_layout(width=80)

    output = Output(width=80, height=24)
    # Pass style as empty dict since we're testing basic rendering
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})

    result = output.get()["output"]
    assert "Hello" in result


def test_render_nested_nodes():
    """Test rendering nested box and text nodes"""
    root = YogaNode()
    root.set_style({"width": 80, "height": 24, "flexDirection": "column"})

    box = YogaNode()
    box.set_style({"width": 20, "height": 5})

    text = TextNode("Nested")
    box.add_child(text)
    root.add_child(box)

    root.calculate_layout(width=80)

    output = Output(width=80, height=24)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})

    result = output.get()["output"]
    assert "Nested" in result


def test_render_with_background():
    """Test rendering box with background color"""
    root = YogaNode()
    root.set_style({"width": 20, "height": 5})

    root.calculate_layout(width=20)

    output = Output(width=20, height=5)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={"backgroundColor": "blue"})

    result = output.get()["output"]
    # Should contain background color codes
    assert "\x1b[" in result


def test_render_with_border():
    """Test rendering box with border"""
    root = YogaNode()
    root.set_style({"width": 20, "height": 5})

    root.calculate_layout(width=20)

    output = Output(width=20, height=5)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={"borderStyle": "single"})

    result = output.get()["output"]
    # Should contain border characters
    assert "┌" in result or "│" in result


def test_render_with_padding():
    """Test rendering box with padding"""
    root = YogaNode()
    root.set_style({"width": 20, "height": 5, "padding": 2, "flexDirection": "column"})

    text = TextNode("Padded")
    root.add_child(text)

    root.calculate_layout(width=20)

    output = Output(width=20, height=5)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})

    result = output.get()["output"]
    assert "Padded" in result


def test_render_multiline_text():
    """Test rendering multiline text"""
    root = YogaNode()
    root.set_style({"width": 80, "height": 24})

    text = TextNode("Line1\nLine2")
    root.add_child(text)

    root.calculate_layout(width=80)

    output = Output(width=80, height=24)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})

    result = output.get()["output"]
    assert "Line1" in result
    assert "Line2" in result


def test_apply_padding_to_text():
    """Test applyPaddingToText indents text correctly"""
    from inkpy.renderer.render_node import apply_padding_to_text

    # Test with simple text
    text = "Hello"
    result = apply_padding_to_text(text, offset_x=4, offset_y=2)

    # Should have 2 newlines at start and 4 spaces before "Hello"
    assert result.startswith("\n\n")
    assert "    Hello" in result

    # Test with multiline text
    multiline = "Line1\nLine2"
    result = apply_padding_to_text(multiline, offset_x=2, offset_y=1)

    # Should have 1 newline at start and 2 spaces before each line
    assert result.startswith("\n")
    assert "  Line1" in result
    assert "  Line2" in result


def test_apply_padding_to_text_zero_offset():
    """Test applyPaddingToText with zero offset"""
    from inkpy.renderer.render_node import apply_padding_to_text

    text = "NoOffset"
    result = apply_padding_to_text(text, offset_x=0, offset_y=0)

    # Should return text unchanged
    assert result == "NoOffset"


# --- Task 2: indent-string parity tests ---


def test_indent_string_basic():
    """Test indent_string matches indent-string npm package behavior."""
    from inkpy.renderer.render_node import indent_string

    text = "Hello"
    result = indent_string(text, 4)
    assert result == "    Hello"


def test_indent_string_multiline():
    """Test indent_string indents each line."""
    from inkpy.renderer.render_node import indent_string

    text = "Line1\nLine2\nLine3"
    result = indent_string(text, 2)

    lines = result.split("\n")
    assert lines[0] == "  Line1"
    assert lines[1] == "  Line2"
    assert lines[2] == "  Line3"


def test_indent_string_zero():
    """Test indent_string with zero indent returns unchanged."""
    from inkpy.renderer.render_node import indent_string

    text = "NoIndent"
    result = indent_string(text, 0)
    assert result == "NoIndent"


def test_indent_string_negative():
    """Test indent_string with negative indent returns unchanged."""
    from inkpy.renderer.render_node import indent_string

    text = "NoIndent"
    result = indent_string(text, -5)
    assert result == "NoIndent"


def test_apply_padding_only_x():
    """Test apply_padding_to_text with only X offset."""
    from inkpy.renderer.render_node import apply_padding_to_text

    text = "Test"
    result = apply_padding_to_text(text, offset_x=3, offset_y=0)
    assert result == "   Test"


def test_apply_padding_only_y():
    """Test apply_padding_to_text with only Y offset."""
    from inkpy.renderer.render_node import apply_padding_to_text

    text = "Test"
    result = apply_padding_to_text(text, offset_x=0, offset_y=2)
    assert result == "\n\nTest"


def test_apply_padding_multiline_with_both():
    """Test apply_padding_to_text with multiline text and both offsets."""
    from inkpy.renderer.render_node import apply_padding_to_text

    text = "A\nB"
    result = apply_padding_to_text(text, offset_x=2, offset_y=1)

    # Should have: \n (1 newline) + "  A\n  B" (indented lines)
    assert result.startswith("\n")
    assert "  A" in result
    assert "  B" in result
