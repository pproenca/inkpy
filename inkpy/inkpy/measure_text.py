"""
Text measurement module - measures text dimensions (width, height)
"""
from typing import Dict
import re

# Cache for text measurements
_cache: Dict[str, Dict[str, int]] = {}

def measure_text(text: str) -> Dict[str, int]:
    """
    Measure text dimensions (width and height).
    
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
    
    # Calculate width (widest line)
    lines = text.split('\n')
    width = 0
    for line in lines:
        # Strip ANSI codes for accurate measurement
        stripped = _strip_ansi(line)
        width = max(width, len(stripped))
    
    # Height is number of lines
    height = len(lines)
    
    dimensions = {'width': width, 'height': height}
    _cache[text] = dimensions
    
    return dimensions

def _strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

