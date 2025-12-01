import pytest
from inkpy.renderer.renderer import Renderer
from inkpy.layout.yoga_node import YogaNode
from inkpy.layout.text_node import TextNode

def test_render_text():
    node = TextNode("Hello")
    # Manually set layout for test
    node.view.set_frame_position_and_size(0, 0, 5, 1)
    
    renderer = Renderer()
    output = renderer.render_node(node)
    
    # Expect ANSI cursor move to 1,1 and "Hello"
    assert "\x1b[1;1H" in output
    assert "Hello" in output

def test_render_colored_text():
    # Not implemented styles yet, but assuming node has style
    # node = TextNode("Hello", style={'color': 'red'}) 
    pass

def test_render_with_layout():
    parent = YogaNode()
    parent.set_style({'width': 20, 'height': 10})
    
    child = TextNode("Hello")
    child.view.set_frame_position_and_size(5, 2, 5, 1) # Relative to parent? Or absolute?
    # Renderer needs absolute coordinates usually.
    # If our layout engine provides relative, Renderer needs to calculate absolute.
    
    # Let's assume get_layout() returns relative, and Renderer traverses to compute absolute.
    
    parent.add_child(child)
    
    renderer = Renderer()
    # Set parent at 0,0
    parent.view.set_frame_position_and_size(0, 0, 20, 10)
    
    output = renderer.render(parent)
    
    # Child should be at 0+5, 0+2 = 5, 2.
    # Terminal coordinates are 1-based? So 3, 6? (row 3, col 6)
    # \x1b[row;colH
    assert "\x1b[3;6H" in output
    assert "Hello" in output

def test_render_nested_boxes():
    # Similar to above but deeper nesting
    pass
