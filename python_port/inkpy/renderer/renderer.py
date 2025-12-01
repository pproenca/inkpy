from typing import List, Optional
from inkpy.layout.yoga_node import YogaNode
from inkpy.layout.text_node import TextNode

class Renderer:
    def __init__(self):
        pass

    def render(self, root: YogaNode) -> str:
        # Traverse tree, compute absolute positions, render nodes
        self.buffer = []
        self._render_tree(root, 0, 0)
        return "".join(self.buffer)

    def _render_tree(self, node: YogaNode, parent_x: float, parent_y: float):
        layout = node.get_layout()
        x = parent_x + layout['left']
        y = parent_y + layout['top']
        
        output = self.render_node(node, x, y)
        if output:
            self.buffer.append(output)
            
        for child in node.children:
            self._render_tree(child, x, y)

    def render_node(self, node: YogaNode, x: float = None, y: float = None) -> Optional[str]:
        if isinstance(node, TextNode):
            text = node.view.text
            if x is None or y is None:
                layout = node.get_layout()
                x = layout['left']
                y = layout['top']
            
            # Convert 0-based to 1-based for ANSI
            row = int(y) + 1
            col = int(x) + 1
            
            # ANSI cursor move: \x1b[row;colH
            return f"\x1b[{row};{col}H{text}"
            
        return None
