"""
TUI Backend - Bridges ReactPy VDOM to DOM node system
"""
from typing import Any, Optional, Dict, List, Callable
from reactpy.core.layout import Layout
import poga
from inkpy.dom import (
    create_node, 
    create_text_node, 
    append_child_node,
    remove_child_node,
    set_style,
    set_attribute,
    set_text_node_value,
    DOMElement,
    TextNode
)
from inkpy.layout.styles import apply_styles


def _diff(before: Dict[str, Any], after: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Diff two dictionaries, returning only changed keys"""
    if before == after:
        return None
    
    if not before:
        return after
    
    changed: Dict[str, Any] = {}
    is_changed = False
    
    # Check for deleted keys
    for key in before.keys():
        if key not in after:
            changed[key] = None
            is_changed = True
    
    # Check for changed/new keys
    for key, value in after.items():
        if before.get(key) != value:
            changed[key] = value
            is_changed = True
    
    return changed if is_changed else None


def _cleanup_yoga_node(node: Optional[Any]):
    """Clean up Yoga node by unsetting measure func and freeing recursively"""
    if node is None:
        return
    
    # Unset measure function if it exists
    if hasattr(node, 'unset_measure_func'):
        try:
            node.unset_measure_func()
        except Exception:
            pass
    
    # Free recursively if method exists
    if hasattr(node, 'free_recursive'):
        try:
            node.free_recursive()
        except Exception:
            pass


class HostContext:
    """Host context for tracking component nesting"""
    def __init__(self, is_inside_text: bool = False):
        self.is_inside_text = is_inside_text
    
    def __eq__(self, other):
        if not isinstance(other, HostContext):
            return False
        return self.is_inside_text == other.is_inside_text


class TUIBackend:
    """Backend that converts ReactPy VDOM to DOM nodes"""
    
    def __init__(self):
        self.root: Optional[DOMElement] = None
        self._layout: Optional[Layout] = None
        self._vdom_to_dom_map: Dict[int, DOMElement] = {}
        self._current_root_node: Optional[DOMElement] = None
    
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
    
    def get_root_host_context(self) -> HostContext:
        """Get root host context (isInsideText=False at root)"""
        return HostContext(is_inside_text=False)
    
    def get_child_host_context(self, parent_context: HostContext, node_type: str) -> HostContext:
        """Get child host context based on parent and node type"""
        previous_is_inside_text = parent_context.is_inside_text
        is_inside_text = node_type in ('ink-text', 'ink-virtual-text')
        
        if previous_is_inside_text == is_inside_text:
            return parent_context
        
        return HostContext(is_inside_text=is_inside_text)
    
    def create_instance(
        self,
        original_type: str,
        new_props: Dict[str, Any],
        root_node: Optional[DOMElement],
        host_context: HostContext
    ) -> DOMElement:
        """Create a DOM instance from component type and props"""
        # Validate nesting: Box cannot be inside Text
        if host_context.is_inside_text and original_type == 'ink-box':
            raise ValueError("<Box> can't be nested inside <Text> component")
        
        # Convert ink-text to ink-virtual-text if already inside text
        node_type = (
            'ink-virtual-text' if (original_type == 'ink-text' and host_context.is_inside_text)
            else original_type
        )
        
        node = create_node(node_type)
        
        # Process props
        for key, value in new_props.items():
            if key == 'children':
                continue
            
            if key == 'style':
                set_style(node, value)
                if node.yoga_node and value:
                    apply_styles(node.yoga_node, value)
                continue
            
            if key == 'internal_transform':
                node.internal_transform = value
                continue
            
            if key == 'internal_static':
                self._current_root_node = root_node
                node.internal_static = True
                if root_node:
                    root_node.is_static_dirty = True
                    root_node.static_node = node
                continue
            
            set_attribute(node, key, value)
        
        return node
    
    def create_text_instance(
        self,
        text: str,
        root_node: Optional[DOMElement],
        host_context: HostContext
    ) -> TextNode:
        """Create a text node instance"""
        if not host_context.is_inside_text:
            raise ValueError(f'Text string "{text}" must be rendered inside <Text> component')
        
        return create_text_node(text)
    
    def commit_update(
        self,
        node: DOMElement,
        node_type: str,
        old_props: Dict[str, Any],
        new_props: Dict[str, Any]
    ):
        """Commit updates to a node by diffing old and new props"""
        # Mark static dirty if this is a static node
        if self._current_root_node and node.internal_static:
            self._current_root_node.is_static_dirty = True
        
        # Diff props
        props_diff = _diff(old_props, new_props)
        style_diff = _diff(
            old_props.get('style', {}),
            new_props.get('style', {})
        )
        
        if not props_diff and not style_diff:
            return
        
        # Apply prop changes
        if props_diff:
            for key, value in props_diff.items():
                if key == 'style':
                    set_style(node, value)
                    continue
                
                if key == 'internal_transform':
                    node.internal_transform = value
                    continue
                
                if key == 'internal_static':
                    node.internal_static = True
                    continue
                
                if value is None:
                    # Remove attribute
                    if key in node.attributes:
                        del node.attributes[key]
                else:
                    set_attribute(node, key, value)
        
        # Apply style changes
        if style_diff and node.yoga_node:
            apply_styles(node.yoga_node, style_diff)
    
    def commit_text_update(self, node: TextNode, old_text: str, new_text: str):
        """Commit text content update"""
        set_text_node_value(node, new_text)
    
    def reset_after_commit(self, root_node: DOMElement):
        """Reset after commit - trigger layout and render callbacks"""
        # Trigger layout callback
        if callable(root_node.on_compute_layout):
            root_node.on_compute_layout()
        
        # Handle static elements - trigger immediate render
        if root_node.is_static_dirty:
            root_node.is_static_dirty = False
            if callable(root_node.on_immediate_render):
                root_node.on_immediate_render()
            return
        
        # Trigger normal render callback
        if callable(root_node.on_render):
            root_node.on_render()
    
    def remove_child(self, parent: DOMElement, child: DOMElement):
        """Remove child from parent and cleanup Yoga node"""
        remove_child_node(parent, child)
        _cleanup_yoga_node(child.yoga_node)
    
    def remove_child_from_container(self, container: DOMElement, child: DOMElement):
        """Remove child from container (alias for remove_child)"""
        self.remove_child(container, child)
    
    def unmount(self):
        """Clean up backend"""
        # Cleanup all Yoga nodes
        if self.root:
            self._cleanup_tree(self.root)
        
        self.root = None
        self._layout = None
        self._vdom_to_dom_map.clear()
        self._current_root_node = None
    
    def _cleanup_tree(self, node: DOMElement):
        """Recursively cleanup Yoga nodes in tree"""
        for child in node.child_nodes:
            if isinstance(child, DOMElement):
                self._cleanup_tree(child)
        _cleanup_yoga_node(node.yoga_node)
    
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
    
    def hide_instance(self, node: DOMElement):
        """Hide element by setting display none"""
        if node.yoga_node:
            layout = node.yoga_node.view.poga_layout()
            layout.display = poga.YGDisplay.DisplayNone
    
    def unhide_instance(self, node: DOMElement):
        """Unhide element by setting display flex"""
        if node.yoga_node:
            layout = node.yoga_node.view.poga_layout()
            layout.display = poga.YGDisplay.Flex
    
    def hide_text_instance(self, node: TextNode):
        """Hide text by setting value to empty string"""
        set_text_node_value(node, '')
    
    def unhide_text_instance(self, node: TextNode, text: str):
        """Unhide text by restoring value"""
        set_text_node_value(node, text)
    
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
