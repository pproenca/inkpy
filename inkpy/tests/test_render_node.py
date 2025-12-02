from inkpy.renderer.render_node import render_node_to_output
from inkpy.renderer.output import Output
from inkpy.layout.yoga_node import YogaNode
from inkpy.layout.text_node import TextNode


def test_render_text_node():
    """Test rendering a simple text node"""
    root = YogaNode()
    root.set_style({'width': 80, 'height': 24})
    
    text_node = TextNode("Hello")
    root.add_child(text_node)
    
    root.calculate_layout(width=80)
    
    output = Output(width=80, height=24)
    # Pass style as empty dict since we're testing basic rendering
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})
    
    result = output.get()['output']
    assert "Hello" in result


def test_render_nested_nodes():
    """Test rendering nested box and text nodes"""
    root = YogaNode()
    root.set_style({'width': 80, 'height': 24, 'flexDirection': 'column'})
    
    box = YogaNode()
    box.set_style({'width': 20, 'height': 5})
    
    text = TextNode("Nested")
    box.add_child(text)
    root.add_child(box)
    
    root.calculate_layout(width=80)
    
    output = Output(width=80, height=24)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})
    
    result = output.get()['output']
    assert "Nested" in result


def test_render_with_background():
    """Test rendering box with background color"""
    root = YogaNode()
    root.set_style({'width': 20, 'height': 5})
    
    root.calculate_layout(width=20)
    
    output = Output(width=20, height=5)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={'backgroundColor': 'blue'})
    
    result = output.get()['output']
    # Should contain background color codes
    assert '\x1b[' in result


def test_render_with_border():
    """Test rendering box with border"""
    root = YogaNode()
    root.set_style({'width': 20, 'height': 5})
    
    root.calculate_layout(width=20)
    
    output = Output(width=20, height=5)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={'borderStyle': 'single'})
    
    result = output.get()['output']
    # Should contain border characters
    assert '┌' in result or '│' in result


def test_render_with_padding():
    """Test rendering box with padding"""
    root = YogaNode()
    root.set_style({
        'width': 20,
        'height': 5,
        'padding': 2,
        'flexDirection': 'column'
    })
    
    text = TextNode("Padded")
    root.add_child(text)
    
    root.calculate_layout(width=20)
    
    output = Output(width=20, height=5)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})
    
    result = output.get()['output']
    assert "Padded" in result


def test_render_multiline_text():
    """Test rendering multiline text"""
    root = YogaNode()
    root.set_style({'width': 80, 'height': 24})
    
    text = TextNode("Line1\nLine2")
    root.add_child(text)
    
    root.calculate_layout(width=80)
    
    output = Output(width=80, height=24)
    render_node_to_output(root, output, offset_x=0, offset_y=0, style={})
    
    result = output.get()['output']
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

