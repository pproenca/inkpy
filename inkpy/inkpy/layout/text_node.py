from typing import Tuple
import math
from .yoga_node import YogaNode, NodeView

class TextNodeView(NodeView):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        
    def size_that_fits(self, width: float, height: float) -> Tuple[float, float]:
        return self.measure_text(width)

    def measure_text(self, max_width: float) -> Tuple[float, float]:
        # Simple implementation for now:
        # 1. Split by newlines
        # 2. If max_width is defined, wrap lines
        # 3. Calculate max line length (width) and number of lines (height)
        
        lines = self.text.split('\n')
        
        if math.isnan(max_width):
            # No wrapping
            final_lines = lines
        else:
            final_lines = []
            for line in lines:
                # Simple wrapping logic
                if len(line) <= max_width:
                    final_lines.append(line)
                else:
                    # Break into chunks
                    # This is a very naive word wrapping, assumes 1 char = 1 unit width
                    # Does not handle word boundaries yet
                    for i in range(0, len(line), int(max_width)):
                        final_lines.append(line[i:i+int(max_width)])
        
        # Remove ANSI codes for measurement if we were doing that
        # For now assuming plain text or that we need to implement stripping
        
        width = 0
        for line in final_lines:
            # Strip ANSI codes for accurate character count
            stripped = self._strip_ansi(line)
            width = max(width, len(stripped))
            
        height = len(final_lines)
        
        return (float(width), float(height))

    def _strip_ansi(self, text: str) -> str:
        # Simple stripper or regex
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

class TextNode(YogaNode):
    def __init__(self, text: str):
        # We need to override the view creation
        self.view = TextNodeView(text)
        self.children = [] # Text nodes usually don't have children?
        
    def set_text(self, text: str):
        self.view.text = text
        # Trigger layout recalc if needed?
        self.view.poga_layout().mark_dirty()

    def measure(self, width: float = float('nan'), height: float = float('nan')) -> Tuple[float, float]:
        # Helper for tests, direct access to measurement logic
        return self.view.size_that_fits(width, height)
