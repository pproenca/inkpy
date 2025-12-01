import pytest
from inkpy.layout.text_node import TextNode
from inkpy.layout.yoga_node import YogaNode

def test_text_measurement_simple():
    text_node = TextNode("Hello World")
    # Yoga usually requires a parent to layout, but measure function is internal
    # We might need to wrap it in a YogaNode or TextNode inherits from YogaNode
    
    # Let's assume TextNode IS a YogaNode that has a custom measure function
    size = text_node.measure(float('nan'), float('nan'))
    assert size[0] == 11  # width
    assert size[1] == 1   # height

def test_multiline_text():
    text_node = TextNode("Hello\nWorld")
    size = text_node.measure(float('nan'), float('nan'))
    assert size[0] == 5  # max width ("Hello" or "World")
    assert size[1] == 2  # lines

def test_text_wrapping():
    # constrained width
    text_node = TextNode("Hello World")
    # If we constrain width to 8, "Hello World" (11 chars) should wrap
    # "Hello" (5)
    # "World" (5)
    size = text_node.measure(8, float('nan'))
    assert size[0] <= 8
    assert size[1] == 2

def test_ansi_escape_codes_ignored_in_width():
    # \x1b[31m is red color (5 chars), but takes 0 space
    text = "\x1b[31mHello\x1b[0m" 
    text_node = TextNode(text)
    size = text_node.measure(float('nan'), float('nan'))
    assert size[0] == 5  # "Hello" length
    assert size[1] == 1

def test_unicode_width():
    # Some unicode chars are full width (2 cells)
    # For now, let's assume standard 1-char width unless we use wcwidth
    # Ideally we should support it, but basic implementation might just use len()
    pass

def test_integration_with_layout():
    root = YogaNode()
    root.set_style({'width': 100, 'height': 100})
    
    text_node = TextNode("Hello World")
    root.add_child(text_node)
    
    root.calculate_layout()
    
    layout = text_node.get_layout()
    assert layout['width'] == 11
    assert layout['height'] == 1
