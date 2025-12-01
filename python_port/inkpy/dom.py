"""
DOM node system - represents the virtual DOM tree for InkPy
"""
from typing import Optional, List, Dict, Any, Union, Callable
from inkpy.layout.yoga_node import YogaNode
from inkpy.measure_text import measure_text
from inkpy.wrap_text import wrap_text

# Type definitions
NodeName = Union[str, type]  # 'ink-root', 'ink-box', 'ink-text', 'ink-virtual-text', '#text'

class DOMNode:
    """Base class for DOM nodes"""
    def __init__(self):
        self.node_name: str = ''
        self.parent_node: Optional['DOMElement'] = None
        self.yoga_node: Optional[YogaNode] = None
        self.style: Dict[str, Any] = {}
        self.internal_static: bool = False

class DOMElement(DOMNode):
    """DOM element node"""
    def __init__(self, node_name: str):
        super().__init__()
        self.node_name = node_name
        self.attributes: Dict[str, Any] = {}
        self.child_nodes: List[Union['DOMElement', 'TextNode']] = []
        self.internal_transform: Optional[Callable] = None
        self.internal_accessibility: Dict[str, Any] = {}
        self.is_static_dirty: bool = False
        self.static_node: Optional['DOMElement'] = None
        self.on_compute_layout: Optional[Callable] = None
        self.on_render: Optional[Callable] = None
        self.on_immediate_render: Optional[Callable] = None

class TextNode(DOMNode):
    """Text node"""
    def __init__(self, value: str):
        super().__init__()
        self.node_name = '#text'
        self.node_value = value

# Factory functions
def create_node(node_name: str) -> DOMElement:
    """Create a DOM element node"""
    node = DOMElement(node_name)
    
    # Create Yoga node (except for virtual text)
    if node_name != 'ink-virtual-text':
        node.yoga_node = YogaNode()
    
    # Set measure function for text nodes
    if node_name == 'ink-text':
        def measure_func(width: float, height: float) -> Dict[str, float]:
            return measure_text_node(node, width, height)
        # Note: YogaNode doesn't have set_measure_func yet, we'll need to add it
        # For now, we'll store it and set it when needed
        node._measure_func = measure_func
    
    return node

def create_text_node(text: str) -> TextNode:
    """Create a text node"""
    if not isinstance(text, str):
        text = str(text)
    node = TextNode(text)
    return node

def append_child_node(parent: DOMElement, child: Union[DOMElement, TextNode]):
    """Append a child node to parent"""
    # Remove from previous parent if exists
    if child.parent_node:
        remove_child_node(child.parent_node, child)
    
    child.parent_node = parent
    parent.child_nodes.append(child)
    
    # Update Yoga tree
    if isinstance(child, DOMElement) and child.yoga_node and parent.yoga_node:
        parent.yoga_node.add_child(child.yoga_node)
    
    # Mark text nodes as dirty
    if parent.node_name in ('ink-text', 'ink-virtual-text'):
        mark_node_as_dirty(parent)

def insert_before_node(parent: DOMElement, new_child: Union[DOMElement, TextNode], before_child: Union[DOMElement, TextNode]):
    """Insert new_child before before_child"""
    if new_child.parent_node:
        remove_child_node(new_child.parent_node, new_child)
    
    new_child.parent_node = parent
    
    try:
        index = parent.child_nodes.index(before_child)
        parent.child_nodes.insert(index, new_child)
        
        # Update Yoga tree - need to remove and re-add to maintain order
        if isinstance(new_child, DOMElement) and new_child.yoga_node and parent.yoga_node:
            # Remove all children and re-add in correct order
            # This is inefficient but necessary for correct ordering
            yoga_children = []
            for c in parent.child_nodes:
                if isinstance(c, DOMElement) and c.yoga_node:
                    yoga_children.append(c.yoga_node)
            
            # Clear and re-add
            for yoga_child in parent.yoga_node.children[:]:
                parent.yoga_node.remove_child(yoga_child)
            
            for yoga_child in yoga_children:
                parent.yoga_node.add_child(yoga_child)
    except ValueError:
        # before_child not found, append instead
        parent.child_nodes.append(new_child)
        if isinstance(new_child, DOMElement) and new_child.yoga_node and parent.yoga_node:
            parent.yoga_node.add_child(new_child.yoga_node)
    
    if parent.node_name in ('ink-text', 'ink-virtual-text'):
        mark_node_as_dirty(parent)

def remove_child_node(parent: DOMElement, child: Union[DOMElement, TextNode]):
    """Remove child node from parent"""
    if isinstance(child, DOMElement) and child.yoga_node and parent.yoga_node:
        parent.yoga_node.remove_child(child.yoga_node)
    
    child.parent_node = None
    
    try:
        parent.child_nodes.remove(child)
    except ValueError:
        pass
    
    if parent.node_name in ('ink-text', 'ink-virtual-text'):
        mark_node_as_dirty(parent)

def set_attribute(node: DOMElement, key: str, value: Any):
    """Set attribute on node"""
    if key == 'internal_accessibility':
        node.internal_accessibility = value
    else:
        node.attributes[key] = value

def set_style(node: Union[DOMElement, TextNode], style: Dict[str, Any]):
    """Set style on node"""
    node.style = style
    # Apply style to yoga node if present
    if node.yoga_node:
        node.yoga_node.set_style(style)

def set_text_node_value(node: TextNode, value: str):
    """Set text value on text node"""
    node.node_value = value

# Helper functions
def measure_text_node(node: Union[DOMElement, TextNode], width: float, height: float) -> Dict[str, float]:
    """Measure text node dimensions"""
    # Get text content
    if isinstance(node, TextNode):
        text = node.node_value
    else:
        text = squash_text_nodes(node)
    
    dimensions = measure_text(text)
    
    # Text fits, no need to wrap
    if dimensions['width'] <= width:
        return {'width': float(dimensions['width']), 'height': float(dimensions['height'])}
    
    # Handle edge case when width < 1px
    if dimensions['width'] >= 1 and 0 < width < 1:
        return {'width': float(dimensions['width']), 'height': float(dimensions['height'])}
    
    # Wrap text
    text_wrap = node.style.get('textWrap', 'wrap')
    wrapped_text = wrap_text(text, width, text_wrap)
    
    wrapped_dimensions = measure_text(wrapped_text)
    return {'width': float(wrapped_dimensions['width']), 'height': float(wrapped_dimensions['height'])}

def find_closest_yoga_node(node: Optional[Union[DOMElement, TextNode]]) -> Optional[YogaNode]:
    """Find closest parent with Yoga node"""
    if not node or not node.parent_node:
        return None
    
    if node.yoga_node:
        return node.yoga_node
    
    return find_closest_yoga_node(node.parent_node)

def mark_node_as_dirty(node: Optional[Union[DOMElement, TextNode]]):
    """Mark closest Yoga node as dirty for remeasurement"""
    yoga_node = find_closest_yoga_node(node)
    if yoga_node:
        # Mark dirty by accessing the layout
        yoga_node.view.poga_layout().mark_dirty()

def squash_text_nodes(node: DOMElement) -> str:
    """
    Concatenate all text node children into a single string.
    
    This allows combining multiple text nodes into one and writing
    to Output instance only once. For example, <Text>hello{' '}world</Text>
    is actually 3 text nodes, which would result in 3 writes to Output.
    
    Args:
        node: DOM element node
        
    Returns:
        Concatenated text string
    """
    text = ''
    
    for index, child_node in enumerate(node.child_nodes):
        if child_node is None:
            continue
        
        node_text = ''
        
        if isinstance(child_node, TextNode):
            node_text = child_node.node_value
        elif isinstance(child_node, DOMElement):
            if child_node.node_name in ('ink-text', 'ink-virtual-text'):
                node_text = squash_text_nodes(child_node)
            
            # Apply transform if present
            if len(node_text) > 0 and callable(getattr(child_node, 'internal_transform', None)):
                node_text = child_node.internal_transform(node_text, index)
        
        text += node_text
    
    return text

