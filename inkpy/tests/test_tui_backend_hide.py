"""
Tests for TUIBackend hide/unhide instance methods.

Following TDD: Write failing test first, then implement.
"""
from inkpy.backend.tui_backend import TUIBackend
from inkpy.dom import create_node, create_text_node
import poga


def test_hide_instance_sets_display_none():
    """Test that hide_instance sets display to none"""
    backend = TUIBackend()
    node = create_node('ink-box')
    
    # Ensure node has yoga_node
    assert node.yoga_node is not None
    
    # Hide the instance
    backend.hide_instance(node)
    
    # Display should be set to none
    layout = node.yoga_node.view.poga_layout()
    assert layout.display == poga.YGDisplay.DisplayNone


def test_unhide_instance_sets_display_flex():
    """Test that unhide_instance sets display to flex"""
    backend = TUIBackend()
    node = create_node('ink-box')
    
    # First hide it
    backend.hide_instance(node)
    layout = node.yoga_node.view.poga_layout()
    assert layout.display == poga.YGDisplay.DisplayNone
    
    # Then unhide it
    backend.unhide_instance(node)
    
    # Display should be set to flex
    assert layout.display == poga.YGDisplay.Flex


def test_hide_instance_handles_no_yoga_node():
    """Test that hide_instance handles nodes without yoga_node gracefully"""
    backend = TUIBackend()
    # Create a node that might not have yoga_node (edge case)
    # Actually, create_node always creates yoga_node, so this test verifies robustness
    node = create_node('ink-box')
    # Manually remove yoga_node to test edge case
    original_yoga = node.yoga_node
    node.yoga_node = None
    
    # Should not raise error
    backend.hide_instance(node)
    
    # Restore for cleanup
    node.yoga_node = original_yoga


def test_unhide_instance_handles_no_yoga_node():
    """Test that unhide_instance handles nodes without yoga_node gracefully"""
    backend = TUIBackend()
    node = create_node('ink-box')
    original_yoga = node.yoga_node
    node.yoga_node = None
    
    # Should not raise error
    backend.unhide_instance(node)
    
    # Restore for cleanup
    node.yoga_node = original_yoga


def test_hide_text_instance_sets_empty_string():
    """Test that hide_text_instance sets text value to empty string"""
    backend = TUIBackend()
    text_node = create_text_node("Hello World")
    
    # Verify initial text (TextNode stores text in node_value)
    assert text_node.node_value == "Hello World"
    
    # Hide the text instance
    backend.hide_text_instance(text_node)
    
    # Text value should be empty
    assert text_node.node_value == ""


def test_unhide_text_instance_restores_text():
    """Test that unhide_text_instance restores text value"""
    backend = TUIBackend()
    original_text = "Hello World"
    text_node = create_text_node(original_text)
    
    # Verify initial text
    assert text_node.node_value == original_text
    
    # First hide it
    backend.hide_text_instance(text_node)
    assert text_node.node_value == ""
    
    # Then unhide it with new text
    new_text = "Restored Text"
    backend.unhide_text_instance(text_node, new_text)
    
    # Text should be restored
    assert text_node.node_value == new_text


def test_unhide_text_instance_restores_original_text():
    """Test that unhide_text_instance can restore original text"""
    backend = TUIBackend()
    original_text = "Original Text"
    text_node = create_text_node(original_text)
    
    # Verify initial text
    assert text_node.node_value == original_text
    
    # Hide and then restore with original text
    backend.hide_text_instance(text_node)
    assert text_node.node_value == ""
    
    backend.unhide_text_instance(text_node, original_text)
    
    # Text should match original
    assert text_node.node_value == original_text

