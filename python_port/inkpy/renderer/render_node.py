"""
Render node to output module.

Ports render-node-to-output functionality from Ink.
Traverses the layout tree and renders nodes to the output buffer.
"""
from typing import List, Optional, Callable, Dict, Any
from ..layout.yoga_node import YogaNode
from ..layout.text_node import TextNode
from .output import Output
from .background import render_background
from .borders import render_border
from .colorize import colorize

OutputTransformer = Callable[[str, int], str]


def squash_text_nodes(node: YogaNode) -> str:
    """
    Combine all text nodes in a container into a single string.
    
    Args:
        node: Container node with text children
    
    Returns:
        Combined text string
    """
    text = ''
    for child in node.children:
        if isinstance(child, TextNode):
            text += child.view.text
        elif isinstance(child, YogaNode):
            # Recursively get text from nested containers
            text += squash_text_nodes(child)
    return text


def get_max_width(yoga_node: YogaNode) -> float:
    """
    Get maximum width for text wrapping.
    
    Args:
        yoga_node: Node to get width from
    
    Returns:
        Maximum width in characters
    """
    layout = yoga_node.get_layout()
    return layout.get('width', float('inf'))


def wrap_text_simple(text: str, max_width: float, wrap_type: str = 'wrap') -> str:
    """
    Simple text wrapping implementation.
    
    Args:
        text: Text to wrap
        max_width: Maximum width
        wrap_type: 'wrap' or 'truncate-end', 'truncate-middle', 'truncate-start'
    
    Returns:
        Wrapped or truncated text
    """
    if wrap_type.startswith('truncate'):
        if len(text) <= max_width:
            return text
        
        if wrap_type == 'truncate-end':
            return text[:int(max_width) - 1] + '…'
        elif wrap_type == 'truncate-middle':
            half = int(max_width) // 2
            return text[:half - 1] + '…' + text[-(half - 1):]
        elif wrap_type == 'truncate-start':
            return '…' + text[-(int(max_width) - 1):]
        else:
            return text[:int(max_width)]
    
    # Simple wrapping - split by words and wrap
    if wrap_type == 'wrap':
        lines = []
        for line in text.split('\n'):
            if len(line) <= max_width:
                lines.append(line)
            else:
                # Simple word wrapping
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_width:
                        current_line += (' ' if current_line else '') + word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
        return '\n'.join(lines)
    
    return text


def render_node_to_output(
    node: YogaNode,
    output: Output,
    offset_x: float = 0,
    offset_y: float = 0,
    transformers: Optional[List[OutputTransformer]] = None,
    skip_static: bool = False,
    style: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Render a node tree to the output buffer.
    
    Args:
        node: Root node to render
        output: Output buffer to write to
        offset_x: X offset for absolute positioning
        offset_y: Y offset for absolute positioning
        transformers: List of text transformers to apply
        skip_static: Whether to skip static elements
        style: Style dictionary (for background, border, etc.)
    """
    if transformers is None:
        transformers = []
    
    if style is None:
        style = {}
    
    layout = node.get_layout()
    
    # Calculate absolute position
    x = int(offset_x + layout.get('left', 0))
    y = int(offset_y + layout.get('top', 0))
    width = int(layout.get('width', 0))
    height = int(layout.get('height', 0))
    
    # Handle TextNode
    if isinstance(node, TextNode):
        text = node.view.text
        
        if text:
            # Apply text wrapping if needed
            max_width = width if width > 0 else float('inf')
            wrap_type = style.get('textWrap', 'wrap')
            text = wrap_text_simple(text, max_width, wrap_type)
            
            # Apply transformers
            transformed_lines = []
            for idx, line in enumerate(text.split('\n')):
                transformed_line = line
                for transformer in transformers:
                    transformed_line = transformer(transformed_line, idx)
                transformed_lines.append(transformed_line)
            text = '\n'.join(transformed_lines)
            
            output.write(x, y, text, transformers=[])
        return
    
    # Handle YogaNode (box/container)
    # Render background first
    if style.get('backgroundColor'):
        render_background(
            output, x, y, width, height,
            color=style['backgroundColor'],
            borderLeft=bool(style.get('borderStyle') and style.get('borderLeft', True)),
            borderRight=bool(style.get('borderStyle') and style.get('borderRight', True)),
            borderTop=bool(style.get('borderStyle') and style.get('borderTop', True)),
            borderBottom=bool(style.get('borderStyle') and style.get('borderBottom', True)),
        )
    
    # Render border
    if style.get('borderStyle'):
        render_border(
            output, x, y, width, height,
            style=style['borderStyle'],
            borderTop=style.get('borderTop', True),
            borderBottom=style.get('borderBottom', True),
            borderLeft=style.get('borderLeft', True),
            borderRight=style.get('borderRight', True),
            borderColor=style.get('borderColor'),
            borderTopColor=style.get('borderTopColor'),
            borderBottomColor=style.get('borderBottomColor'),
            borderLeftColor=style.get('borderLeftColor'),
            borderRightColor=style.get('borderRightColor'),
        )
    
    # Handle clipping for overflow
    clipped = False
    if style.get('overflow') == 'hidden' or style.get('overflowX') == 'hidden' or style.get('overflowY') == 'hidden':
        clip_x1 = x if (style.get('overflowX') == 'hidden' or style.get('overflow') == 'hidden') else None
        clip_x2 = x + width if (style.get('overflowX') == 'hidden' or style.get('overflow') == 'hidden') else None
        clip_y1 = y if (style.get('overflowY') == 'hidden' or style.get('overflow') == 'hidden') else None
        clip_y2 = y + height if (style.get('overflowY') == 'hidden' or style.get('overflow') == 'hidden') else None
        
        if clip_x1 is not None or clip_y1 is not None:
            output.clip(x1=clip_x1, x2=clip_x2, y1=clip_y1, y2=clip_y2)
            clipped = True
    
    # Render children
    for child in node.children:
        # Get child style if available (simplified - in real implementation would come from DOM)
        child_style = style.get('childStyle', {}) if isinstance(child, YogaNode) else {}
        
        render_node_to_output(
            child,
            output,
            offset_x=x,
            offset_y=y,
            transformers=transformers,
            skip_static=skip_static,
            style=child_style,
        )
    
    # Unclip if we clipped
    if clipped:
        output.unclip()

