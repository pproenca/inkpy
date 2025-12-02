"""
Text measurement module - measures text dimensions (width, height)
Uses ANSI-aware width calculation for accurate terminal display.
"""
from typing import Dict
from inkpy.renderer.ansi_tokenize import string_width

# Cache for text measurements
_cache: Dict[str, Dict[str, int]] = {}


def measure_text(text: str) -> Dict[str, int]:
    """
    Measure text dimensions (width and height).
    
    Uses ANSI-aware width calculation that handles:
    - ANSI escape codes (ignored in width calculation)
    - CJK characters (double-width)
    - Emoji (variable width)
    
    Args:
        text: Text to measure
        
    Returns:
        Dictionary with 'width' and 'height' keys
    """
    if len(text) == 0:
        return {'width': 0, 'height': 0}
    
    # Check cache
    cached = _cache.get(text)
    if cached:
        return cached
    
    # Calculate width (widest line) using ANSI-aware width
    lines = text.split('\n')
    width = 0
    for line in lines:
        line_width = string_width(line)
        width = max(width, line_width)
    
    # Height is number of lines
    height = len(lines)
    
    dimensions = {'width': width, 'height': height}
    _cache[text] = dimensions
    
    return dimensions

