"""
TUI Backend - Bridges ReactPy VDOM to DOM node system
"""
from typing import Any, Optional, Dict, List, Callable
from reactpy.core.layout import Layout
from inkpy.dom import (
    create_node, 
    create_text_node, 
    append_child_node, 
    set_style,
    set_attribute,
    DOMElement,
    TextNode
)
from inkpy.layout.styles import apply_styles


class TUIBackend:
    """Backend that converts ReactPy VDOM to DOM nodes"""
    
    def __init__(self):
        self.root: Optional[DOMElement] = None
        self._layout: Optional[Layout] = None
        self._vdom_to_dom_map: Dict[int, DOMElement] = {}
    
    def mount(self, component) -> DOMElement:
        """Mount a ReactPy component and return root DOM node"""
        self.root = create_node('ink-root')
        
        # Render component to get VDOM
        if hasattr(component, 'render'):
            vdom = component.render()
        else:
            # Component might be a function or callable
            try:
                vdom = component()
            except Exception:
                vdom = None
        
        # Convert VDOM to DOM
        if vdom:
            self.vdom_to_dom(vdom, self.root)
        
        return self.root
    
    def update(self):
        """Handle component updates"""
        # In full implementation, this would:
        # 1. Get updated VDOM from Layout
        # 2. Diff with current DOM
        # 3. Update DOM nodes accordingly
        # For now, this is a placeholder
        pass
    
    def unmount(self):
        """Clean up backend"""
        self.root = None
        self._layout = None
        self._vdom_to_dom_map.clear()
    
    def calculate_layout(self, width: int = 80):
        """Calculate Yoga layout for root node"""
        if self.root and self.root.yoga_node:
            self.root.yoga_node.calculate_layout(width=width)
    
    def render(self) -> str:
        """Render DOM tree to string"""
        # Full implementation would traverse DOM and render to string
        # This will be implemented when integrating with renderer module
        return ""
    
    def vdom_to_dom(self, vdom: Any, parent: Optional[DOMElement] = None) -> Optional[DOMElement]:
        """
        Convert ReactPy VDOM to DOM nodes.
        
        Args:
            vdom: ReactPy VDOM (dict with tagName/attributes/children, or string)
            parent: Parent DOM element to append to
            
        Returns:
            Created DOM element (or None for text nodes)
        """
        # Handle text nodes
        if isinstance(vdom, str):
            text_node = create_text_node(vdom)
            if parent:
                append_child_node(parent, text_node)
            return None
        
        # Handle non-dict VDOM (skip None, numbers, etc.)
        if not isinstance(vdom, dict):
            return None
        
        tag = vdom.get("tagName", "")
        
        # Map ReactPy tags to Ink DOM node names
        node_name_map = {
            'div': 'ink-box',
            'span': 'ink-text',
        }
        
        # Default to ink-box if tag not recognized
        node_name = node_name_map.get(tag, 'ink-box')
        node = create_node(node_name)
        
        # Apply attributes
        attributes = vdom.get("attributes", {})
        for key, value in attributes.items():
            if key == 'style':
                # Apply style to node
                set_style(node, value)
                # Also apply to Yoga node using proper style system
                if node.yoga_node and value:
                    apply_styles(node.yoga_node, value)
            elif key == 'internal_transform':
                # Store transform function for text rendering
                node.internal_transform = value
            elif key == 'internal_static':
                # Mark node as static
                node.internal_static = value
            elif key == 'internal_accessibility':
                # Set accessibility attributes
                set_attribute(node, key, value)
            else:
                # Store other attributes
                set_attribute(node, key, value)
        
        # Process children recursively
        children = vdom.get("children", [])
        if not isinstance(children, list):
            children = [children] if children is not None else []
        
        for child in children:
            if child is not None:
                self.vdom_to_dom(child, node)
        
        # Append to parent if provided
        if parent:
            append_child_node(parent, node)
        
        return node
    
    async def render_loop(self, layout: Layout):
        """Async render loop for ReactPy Layout"""
        async with layout:
            while True:
                update = await layout.render()
                vdom_root = getattr(update, "model", None)
                if vdom_root is None and isinstance(update, dict):
                    vdom_root = update.get("model")
                
                if vdom_root:
                    self.root = create_node('ink-root')
                    self.vdom_to_dom(vdom_root, self.root)
                    self.calculate_layout()
