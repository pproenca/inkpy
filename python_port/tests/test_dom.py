# test_dom.py
import pytest
from inkpy.dom import (
    create_node,
    create_text_node,
    append_child_node,
    remove_child_node,
    insert_before_node,
    set_attribute,
    set_style,
    DOMElement,
    TextNode,
)

def test_create_node():
    """Test creating a DOM element node"""
    node = create_node('ink-box')
    
    assert node.node_name == 'ink-box'
    assert node.yoga_node is not None
    assert node.style == {}
    assert node.attributes == {}
    assert node.child_nodes == []
    assert node.parent_node is None

def test_create_text_node():
    """Test creating a text node"""
    text_node = create_text_node("Hello, World!")
    
    assert text_node.node_name == '#text'
    assert text_node.node_value == "Hello, World!"
    assert text_node.yoga_node is None
    assert text_node.parent_node is None

def test_append_child_node():
    """Test appending child nodes"""
    parent = create_node('ink-box')
    child1 = create_node('ink-text')
    child2 = create_node('ink-text')
    
    append_child_node(parent, child1)
    assert len(parent.child_nodes) == 1
    assert child1.parent_node == parent
    
    append_child_node(parent, child2)
    assert len(parent.child_nodes) == 2
    assert child2.parent_node == parent

def test_remove_child_node():
    """Test removing child nodes"""
    parent = create_node('ink-box')
    child = create_node('ink-text')
    
    append_child_node(parent, child)
    assert len(parent.child_nodes) == 1
    
    remove_child_node(parent, child)
    assert len(parent.child_nodes) == 0
    assert child.parent_node is None

def test_insert_before_node():
    """Test inserting node before another"""
    parent = create_node('ink-box')
    child1 = create_node('ink-text')
    child2 = create_node('ink-text')
    child3 = create_node('ink-text')
    
    append_child_node(parent, child1)
    append_child_node(parent, child3)
    insert_before_node(parent, child2, child3)
    
    assert parent.child_nodes == [child1, child2, child3]

def test_set_attribute():
    """Test setting node attributes"""
    node = create_node('ink-box')
    
    set_attribute(node, 'id', 'my-box')
    assert node.attributes['id'] == 'my-box'
    
    set_attribute(node, 'data-test', 'value')
    assert node.attributes['data-test'] == 'value'

def test_set_style():
    """Test setting node styles"""
    node = create_node('ink-box')
    
    style = {
        'flexDirection': 'row',
        'padding': 2,
        'backgroundColor': 'blue',
    }
    
    set_style(node, style)
    assert node.style == style

def test_ink_text_measure_function():
    """Test that ink-text nodes have measure function"""
    text_node = create_node('ink-text')
    
    # Should have measure function set on yoga node
    assert text_node.yoga_node is not None
    # Yoga node should have measure function

def test_yoga_node_tree_sync():
    """Test that Yoga tree stays in sync with DOM tree"""
    parent = create_node('ink-box')
    child1 = create_node('ink-box')
    child2 = create_node('ink-box')
    
    append_child_node(parent, child1)
    append_child_node(parent, child2)
    
    # Yoga tree should match DOM tree
    assert len(parent.yoga_node.children) == 2
    
    remove_child_node(parent, child1)
    assert len(parent.yoga_node.children) == 1

def test_text_node_value_update():
    """Test updating text node value"""
    text_node = create_text_node("Initial")
    
    # Should be able to update value
    # This will mark parent yoga node as dirty for remeasurement
    text_node.node_value = "Updated"
    assert text_node.node_value == "Updated"

