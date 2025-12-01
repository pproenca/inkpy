"""
Text wrapping module - wraps text to fit within max width
"""
from typing import Dict, Optional
import re

# Cache for wrapped text
_cache: Dict[str, str] = {}

def wrap_text(text: str, max_width: float, wrap_type: str = 'wrap') -> str:
    """
    Wrap text to fit within max width.
    
    Args:
        text: Text to wrap
        max_width: Maximum width
        wrap_type: 'wrap', 'truncate-end', 'truncate-middle', or 'truncate-start'
        
    Returns:
        Wrapped or truncated text
    """
    max_width_int = int(max_width)
    cache_key = f"{text}{max_width_int}{wrap_type}"
    
    cached = _cache.get(cache_key)
    if cached:
        return cached
    
    wrapped_text = text
    
    if wrap_type == 'wrap':
        wrapped_text = _wrap_ansi(text, max_width_int)
    elif wrap_type.startswith('truncate'):
        wrapped_text = _truncate_text(text, max_width_int, wrap_type)
    
    _cache[cache_key] = wrapped_text
    return wrapped_text

def _wrap_ansi(text: str, max_width: int) -> str:
    """
    Wrap text preserving ANSI codes.
    Simple implementation - wraps at word boundaries.
    """
    lines = text.split('\n')
    wrapped_lines = []
    
    for line in lines:
        if len(_strip_ansi(line)) <= max_width:
            wrapped_lines.append(line)
        else:
            # Split into words and wrap
            words = _split_preserving_ansi(line)
            current_line = ''
            
            for word in words:
                word_stripped = _strip_ansi(word)
                current_stripped = _strip_ansi(current_line)
                
                if len(current_stripped) + len(word_stripped) + 1 <= max_width:
                    current_line += (' ' if current_line else '') + word
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            
            if current_line:
                wrapped_lines.append(current_line)
    
    return '\n'.join(wrapped_lines)

def _truncate_text(text: str, max_width: int, truncate_type: str) -> str:
    """Truncate text to max width"""
    stripped = _strip_ansi(text)
    
    if len(stripped) <= max_width:
        return text
    
    if truncate_type == 'truncate-end':
        # Truncate at end, preserve ANSI codes
        truncated = _truncate_preserving_ansi(text, max_width - 1) + '…'
    elif truncate_type == 'truncate-middle':
        half = max_width // 2
        truncated = _truncate_preserving_ansi(text, half - 1) + '…' + _truncate_preserving_ansi(text, -(half - 1))
    elif truncate_type == 'truncate-start':
        truncated = '…' + _truncate_preserving_ansi(text, -(max_width - 1))
    else:
        truncated = _truncate_preserving_ansi(text, max_width)
    
    return truncated

def _strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def _split_preserving_ansi(text: str) -> list:
    """Split text into words while preserving ANSI codes"""
    # Simple word split - can be enhanced
    words = []
    current_word = ''
    in_ansi = False
    
    for char in text:
        if char == '\x1B':
            in_ansi = True
            current_word += char
        elif in_ansi:
            current_word += char
            if char.isalpha() and char >= '@':
                in_ansi = False
        elif char == ' ':
            if current_word:
                words.append(current_word)
                current_word = ''
        else:
            current_word += char
    
    if current_word:
        words.append(current_word)
    
    return words if words else [text]

def _truncate_preserving_ansi(text: str, length: int) -> str:
    """Truncate text preserving ANSI codes"""
    if length < 0:
        # Negative length means from end
        stripped = _strip_ansi(text)
        if len(stripped) <= abs(length):
            return text
        # Keep last abs(length) characters
        return text[-(abs(length) + len(text) - len(stripped)):]
    
    stripped = _strip_ansi(text)
    if len(stripped) <= length:
        return text
    
    # Truncate while preserving ANSI codes
    result = ''
    stripped_count = 0
    
    for char in text:
        if char == '\x1B':
            result += char
            # Skip ANSI sequence
            continue
        if stripped_count < length:
            result += char
            if not re.match(r'\x1B', char):
                stripped_count += 1
        else:
            break
    
    return result

