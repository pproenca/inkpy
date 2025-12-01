"""
TUI Backend - Bridges ReactPy VDOM to DOM node system
"""
from typing import Any, Optional
from reactpy.core.layout import Layout
from inkpy.dom import create_node, create_text_node, append_child_node, DOMElement
from inkpy.layout.yoga_node import YogaNode

class TUIBackend:
    """Backend that converts ReactPy VDOM to DOM nodes"""
    
    def __init__(self):
        self.root: Optional[DOMElement] = None
        self._layout: Optional[Layout] = None
    
    def mount(self, component) -> DOMElement:
        """Mount a ReactPy component and return root DOM node"""
        self.root = create_node('ink-root')
        
        # Render component to get VDOM
        if hasattr(component, 'render'):
            vdom = component.render()
        else:
            # Component might be a function
            try:
                vdom = component()
            except:
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
        pass
    
    def unmount(self):
        """Clean up backend"""
        self.root = None
        self._layout = None
    
    def calculate_layout(self, width: int = 80):
        """Calculate Yoga layout for root node"""
        if self.root and self.root.yoga_node:
            self.root.yoga_node.calculate_layout(width=width)
    
    def render(self) -> str:
        """Render DOM tree to string"""
        # Full implementation would traverse DOM and render to string
        return ""
    
    def vdom_to_dom(self, vdom: Any, parent: Optional[DOMElement] = None) -> Optional[DOMElement]:
        """Convert ReactPy VDOM to DOM nodes"""
        if isinstance(vdom, str):
            text_node = create_text_node(vdom)
            if parent:
                append_child_node(parent, text_node)
            return None
        
        if not isinstance(vdom, dict):
            return None
        
        tag = vdom.get("tagName", "")
        
        # Map ReactPy tags to Ink DOM node names
        node_name_map = {
            'div': 'ink-box',
            'span': 'ink-text',
        }
        
        node_name = node_name_map.get(tag, 'ink-box')
        node = create_node(node_name)
        
        # Apply attributes
        attributes = vdom.get("attributes", {})
        for key, value in attributes.items():
            if key == 'style':
                node.style = value
            else:
                node.attributes[key] = value
        
        # Process children
        children = vdom.get("children", [])
        for child in children:
            self.vdom_to_dom(child, node)
        
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
