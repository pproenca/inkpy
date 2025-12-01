"""
Virtual output buffer for rendering terminal UI.

Handles positioning and saving output of each node in the tree.
Also responsible for applying transformations to each character of the output.
"""
from typing import List, Optional, Callable, Dict, Any
import re
from .ansi_tokenize import (
    slice_ansi,
    string_width,
    tokenize_ansi,
    styled_chars_from_tokens,
    styled_chars_to_string,
)

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
        
        Uses styled characters for proper ANSI code and multi-column character handling.
        
        Returns:
            Dictionary with 'output' (string) and 'height' (int)
        """
        # Initialize 2D buffer with styled character objects
        # Each cell is a StyledChar: {type: 'char', value: str, fullWidth: bool, styles: List[str]}
        output: List[List[Optional[Dict[str, Any]]]] = []
        
        for y in range(self.height):
            row: List[Optional[Dict[str, Any]]] = []
            for x in range(self.width):
                row.append({
                    'type': 'char',
                    'value': ' ',
                    'fullWidth': False,
                    'styles': []
                })
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
                        # Calculate text width using ANSI-aware width calculation
                        max_line_width = max(string_width(line) for line in lines)
                        if x + max_line_width < clip['x1'] or x > clip['x2']:
                            continue
                    
                    if clip_vertically:
                        if y + len(lines) < clip['y1'] or y > clip['y2']:
                            continue
                    
                    # Apply horizontal clipping using ANSI-aware slicing
                    if clip_horizontally:
                        clipped_lines = []
                        for line in lines:
                            line_width = string_width(line)
                            
                            # Calculate visible portion in display width
                            from_width = 0
                            if x < clip['x1']:
                                from_width = clip['x1'] - x
                            
                            to_width = line_width
                            if x + line_width > clip['x2']:
                                to_width = clip['x2'] - x
                            
                            # Slice using ANSI-aware function
                            if from_width > 0 or to_width < line_width:
                                clipped_line = slice_ansi(line, from_width, to_width)
                                clipped_lines.append(clipped_line)
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
                
                # Write lines to buffer using styled characters
                for offset_y, line in enumerate(lines):
                    target_y = y + offset_y
                    if target_y >= self.height:
                        continue
                    
                    current_line = output[target_y]
                    
                    # Convert line to styled characters
                    tokens = tokenize_ansi(line)
                    characters = styled_chars_from_tokens(tokens)
                    
                    offset_x = x
                    
                    for character in characters:
                        if offset_x >= self.width:
                            break
                        
                        # Write styled character to buffer
                        current_line[offset_x] = character
                        
                        # Determine printed width (multi-column characters)
                        char_width = max(1, string_width(character['value']))
                        
                        # For multi-column characters, clear following cells
                        # to avoid stray spaces/artifacts
                        if char_width > 1:
                            for index in range(1, char_width):
                                if offset_x + index < self.width:
                                    current_line[offset_x + index] = {
                                        'type': 'char',
                                        'value': '',
                                        'fullWidth': False,
                                        'styles': character['styles']
                                    }
                        
                        offset_x += char_width
        
        # Convert buffer to string using styled_chars_to_string
        generated_output = []
        for row in output:
            # Filter out None/undefined items (shouldn't happen, but be safe)
            line_without_empty = [
                item for item in row
                if item is not None and item.get('value') is not None
            ]
            
            # Convert styled characters back to string
            line_str = styled_chars_to_string(line_without_empty)
            generated_output.append(line_str.rstrip())
        
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

