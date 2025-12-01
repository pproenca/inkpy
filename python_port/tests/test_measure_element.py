"""
Tests for measure_element module - Get computed dimensions of DOM elements.

Ported from: src/measure-element.ts
"""
from inkpy.measure_element import measure_element
from inkpy.dom import create_node
from inkpy.layout.styles import apply_styles


def test_measure_element_basic():
    """Test measuring element dimensions"""
    node = create_node('ink-box')
    apply_styles(node.yoga_node, {'width': 50, 'height': 10})
    node.yoga_node.calculate_layout(width=50)
    
    result = measure_element(node)
    
    assert result['width'] == 50
    assert result['height'] == 10


def test_measure_element_no_yoga():
    """Test measuring element without yoga node"""
    node = create_node('ink-virtual-text')  # No yoga node
    result = measure_element(node)
    
    assert result['width'] == 0
    assert result['height'] == 0

