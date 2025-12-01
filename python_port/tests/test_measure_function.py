"""
Tests for measure function application on Poga nodes.

Following TDD: Write failing test first, then implement.
"""
import pytest
from inkpy.dom import create_node, DOMElement
from inkpy.layout.yoga_node import YogaNode
import poga


def test_ink_text_node_has_measure_function():
    """Test that ink-text nodes have measure function set"""
    node = create_node('ink-text')
    
    # Should have yoga_node
    assert node.yoga_node is not None
    
    # Should have measure function stored
    assert hasattr(node, '_measure_func')
    assert node._measure_func is not None


def test_ink_text_node_view_uses_measure_function():
    """Test that ink-text node view uses measure function via size_that_fits"""
    from inkpy.dom import create_text_node, append_child_node
    node = create_node('ink-text')
    # Add a text node as child (ink-text nodes get text from children)
    text_child = create_text_node("Hello World")
    append_child_node(node, text_child)
    
    # The view's size_that_fits should use the measure function
    view = node.yoga_node.view
    size = view.size_that_fits(100.0, 100.0)
    
    # Should return non-zero size for text
    assert size[0] > 0  # width
    assert size[1] > 0  # height


def test_ink_text_node_measure_function_handles_wrapping():
    """Test that measure function handles text wrapping"""
    node = create_node('ink-text')
    node.node_value = "Hello World"
    
    # Measure with narrow width should wrap
    view = node.yoga_node.view
    size_narrow = view.size_that_fits(5.0, 100.0)
    size_wide = view.size_that_fits(100.0, 100.0)
    
    # Narrow width should result in more height (wrapping)
    assert size_narrow[1] >= size_wide[1]


def test_ink_text_node_remeasures_when_content_changes():
    """Test that text nodes are re-measured when content changes"""
    from inkpy.dom import create_text_node, append_child_node, set_text_node_value
    node = create_node('ink-text')
    text_child = create_text_node("Short")
    append_child_node(node, text_child)
    
    view = node.yoga_node.view
    size_short = view.size_that_fits(100.0, 100.0)
    
    # Change content
    set_text_node_value(text_child, "This is a much longer text string")
    size_long = view.size_that_fits(100.0, 100.0)
    
    # Longer text should have different size
    assert size_long[0] > size_short[0] or size_long[1] > size_short[1]


def test_non_text_node_does_not_have_measure_function():
    """Test that non-text nodes don't have measure function"""
    node = create_node('ink-box')
    
    # Should not have measure function
    assert not hasattr(node, '_measure_func') or node._measure_func is None


def test_ink_text_node_measure_function_handles_ansi_codes():
    """Test that measure function handles ANSI codes correctly"""
    from inkpy.dom import create_text_node, append_child_node
    node = create_node('ink-text')
    text_child = create_text_node("\x1b[31mHello\x1b[0m World")
    append_child_node(node, text_child)
    
    view = node.yoga_node.view
    size = view.size_that_fits(100.0, 100.0)
    
    # Should measure correctly ignoring ANSI codes
    # "Hello World" is 11 characters, so width should be around 11
    assert size[0] >= 11

