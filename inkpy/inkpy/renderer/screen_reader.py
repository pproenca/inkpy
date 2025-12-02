"""
Screen reader output module.

Ports render-node-to-screen-reader-output functionality from Ink.
Renders DOM tree to accessible text output for screen readers.
"""
from typing import Optional
from ..dom import DOMElement, squash_text_nodes


def render_node_to_screen_reader_output(
    node: DOMElement,
    skip_static: bool = False,
    parent_role: Optional[str] = None,
) -> str:
    """
    Render node tree to screen reader accessible text.
    
    Args:
        node: Root DOM element node
        skip_static: Whether to skip static elements
        parent_role: Role of parent node (for role inheritance)
    
    Returns:
        Accessible text string for screen readers
    """
    # Skip static elements if requested
    if skip_static and node.internal_static:
        return ''
    
    # Skip nodes with display: none
    if node.style.get('display') == 'none':
        return ''
    
    output = ''
    
    # Handle text nodes
    if node.node_name == 'ink-text':
        output = squash_text_nodes(node)
    
    # Handle box/root nodes
    elif node.node_name in ('ink-box', 'ink-root'):
        # Determine separator based on flex direction
        flex_direction = node.style.get('flexDirection', 'column')
        separator = (
            ' ' if flex_direction in ('row', 'row-reverse')
            else '\n'
        )
        
        # Get child nodes (reverse if needed)
        child_nodes = list(node.child_nodes)
        if flex_direction in ('row-reverse', 'column-reverse'):
            child_nodes = list(reversed(child_nodes))
        
        # Render each child recursively
        child_outputs = []
        for child_node in child_nodes:
            if isinstance(child_node, DOMElement):
                child_output = render_node_to_screen_reader_output(
                    child_node,
                    skip_static=skip_static,
                    parent_role=node.internal_accessibility.get('role') if node.internal_accessibility else None,
                )
                if child_output:
                    child_outputs.append(child_output)
        
        output = separator.join(child_outputs)
    
    # If no output yet, return empty string
    if not output:
        return ''
    
    # Add accessibility annotations
    if node.internal_accessibility:
        role = node.internal_accessibility.get('role')
        state = node.internal_accessibility.get('state', {})
        
        # Add state description
        if state:
            state_keys = [key for key, value in state.items() if value]
            state_description = ', '.join(state_keys)
            
            if state_description:
                output = f"({state_description}) {output}"
        
        # Add role annotation (if different from parent)
        if role and role != parent_role:
            output = f"{role}: {output}"
    
    return output

