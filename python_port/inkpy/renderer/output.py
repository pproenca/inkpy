"""
Virtual output buffer for rendering terminal UI.

Handles positioning and saving output of each node in the tree.
Also responsible for applying transformations to each character of the output.
"""
from typing import List, Optional, Callable, Dict, Any
import re

# Type alias for output transformers
OutputTransformer = Callable[[str, int], str]


class Output:
    """
    Virtual output buffer that handles text positioning, clipping, and transformations.
    
    Used to generate final output of all nodes before writing to actual output stream.
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize output buffer.
        
        Args:
            width: Width of the output buffer in characters
            height: Height of the output buffer in lines
        """
        self.width = width
        self.height = height
        self._operations: List[Dict[str, Any]] = []
    
    def write(
        self,
        x: int,
        y: int,
        text: str,
        transformers: Optional[List[OutputTransformer]] = None
    ) -> None:
        """
        Write text at specified coordinates.
        
        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
            text: Text to write (can contain newlines)
            transformers: Optional list of transformer functions
        """
        if not text:
            return
        
        if transformers is None:
            transformers = []
        
        self._operations.append({
            'type': 'write',
            'x': x,
            'y': y,
            'text': text,
            'transformers': transformers
        })
    
    def clip(
        self,
        x1: Optional[int] = None,
        x2: Optional[int] = None,
        y1: Optional[int] = None,
        y2: Optional[int] = None
    ) -> None:
        """
        Enable clipping region.
        
        Args:
            x1: Left boundary (inclusive)
            x2: Right boundary (inclusive)
            y1: Top boundary (inclusive)
            y2: Bottom boundary (inclusive)
        """
        self._operations.append({
            'type': 'clip',
            'clip': {
                'x1': x1,
                'x2': x2,
                'y1': y1,
                'y2': y2
            }
        })
    
    def unclip(self) -> None:
        """Remove the most recent clipping region."""
        self._operations.append({
            'type': 'unclip'
        })
    
    def get(self) -> Dict[str, Any]:
        """
        Generate final output string from all operations.
        
        Returns:
            Dictionary with 'output' (string) and 'height' (int)
        """
        # Initialize 2D buffer with spaces
        # Each cell is a character (we'll handle ANSI codes separately)
        output: List[List[str]] = []
        
        for y in range(self.height):
            row = [' '] * self.width
            output.append(row)
        
        clips: List[Dict[str, Optional[int]]] = []
        
        for operation in self._operations:
            if operation['type'] == 'clip':
                clips.append(operation['clip'])
            
            elif operation['type'] == 'unclip':
                if clips:
                    clips.pop()
            
            elif operation['type'] == 'write':
                text = operation['text']
                transformers = operation.get('transformers', [])
                x = operation['x']
                y = operation['y']
                lines = text.split('\n')
                
                # Apply clipping if active
                clip = clips[-1] if clips else None
                
                if clip:
                    clip_horizontally = (
                        clip.get('x1') is not None and
                        clip.get('x2') is not None
                    )
                    clip_vertically = (
                        clip.get('y1') is not None and
                        clip.get('y2') is not None
                    )
                    
                    # Skip if completely outside clipping area
                    if clip_horizontally:
                        # Calculate text width (simplified - doesn't handle ANSI codes perfectly)
                        max_line_width = max(len(self._strip_ansi(line)) for line in lines)
                        if x + max_line_width < clip['x1'] or x > clip['x2']:
                            continue
                    
                    if clip_vertically:
                        if y + len(lines) < clip['y1'] or y > clip['y2']:
                            continue
                    
                    # Apply horizontal clipping
                    if clip_horizontally:
                        clipped_lines = []
                        for line in lines:
                            stripped = self._strip_ansi(line)
                            line_width = len(stripped)
                            
                            # Calculate visible portion
                            from_idx = 0
                            if x < clip['x1']:
                                from_idx = clip['x1'] - x
                            
                            to_idx = line_width
                            if x + line_width > clip['x2']:
                                to_idx = clip['x2'] - x + 1
                            
                            # Slice the line (preserving ANSI codes approximately)
                            if from_idx > 0 or to_idx < line_width:
                                # Simple slicing - doesn't perfectly preserve ANSI codes
                                clipped_lines.append(line[from_idx:to_idx])
                            else:
                                clipped_lines.append(line)
                        
                        lines = clipped_lines
                        
                        if x < clip['x1']:
                            x = clip['x1']
                    
                    # Apply vertical clipping
                    if clip_vertically:
                        from_line = 0
                        if y < clip['y1']:
                            from_line = clip['y1'] - y
                        
                        to_line = len(lines)
                        if y + len(lines) > clip['y2']:
                            to_line = clip['y2'] - y + 1
                        
                        lines = lines[from_line:to_line]
                        
                        if y < clip['y1']:
                            y = clip['y1']
                
                # Apply transformers
                for transformer in transformers:
                    transformed_lines = []
                    for idx, line in enumerate(lines):
                        transformed_lines.append(transformer(line, idx))
                    lines = transformed_lines
                
                # Write lines to buffer
                for offset_y, line in enumerate(lines):
                    target_y = y + offset_y
                    if target_y >= self.height:
                        continue
                    
                    current_line = output[target_y]
                    
                    # Write characters to buffer
                    # Handle ANSI codes by writing them as-is
                    # This is simplified - proper handling would parse and reapply
                    char_idx = 0
                    x_pos = x
                    
                    # Simple character-by-character writing
                    # For now, we'll just write the line directly
                    # Proper implementation would parse ANSI codes
                    line_chars = list(line)
                    for char in line_chars:
                        if x_pos >= self.width:
                            break
                        current_line[x_pos] = char
                        x_pos += 1
        
        # Convert buffer to string
        generated_output = []
        for row in output:
            # Join row and trim trailing spaces
            line = ''.join(row).rstrip()
            generated_output.append(line)
        
        return {
            'output': '\n'.join(generated_output),
            'height': len(generated_output)
        }
    
    @staticmethod
    def _strip_ansi(text: str) -> str:
        """
        Strip ANSI escape codes from text for width calculation.
        
        Args:
            text: Text potentially containing ANSI codes
            
        Returns:
            Text with ANSI codes removed
        """
        # Simple ANSI escape sequence regex
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

