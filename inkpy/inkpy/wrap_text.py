"""
Text wrapping module - wraps text to fit within max width

Uses ANSI tokenizer for proper ANSI-aware wrapping and truncation.
"""
from typing import Dict
import re
from .renderer.ansi_tokenize import string_width, slice_ansi, tokenize_ansi

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
    import math
    
    # Handle NaN and infinite values
    if math.isnan(max_width) or math.isinf(max_width):
        return text
    
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
    Wrap text preserving ANSI codes using ANSI-aware width calculation.
    Wraps at word boundaries when possible, falls back to character boundaries for CJK.
    """
    lines = text.split('\n')
    wrapped_lines = []
    
    for line in lines:
        line_width = string_width(line)
        if line_width <= max_width:
            wrapped_lines.append(line)
        else:
            # Split into words and wrap using ANSI-aware width
            words = _split_preserving_ansi(line)
            current_line = ''
            
            for word in words:
                word_width = string_width(word)
                current_width = string_width(current_line)
                space_width = 1 if current_line else 0
                
                if current_width + space_width + word_width <= max_width:
                    # Word fits on current line
                    current_line += (' ' if current_line else '') + word
                elif word_width <= max_width:
                    # Word doesn't fit, but is smaller than max_width
                    # Start new line with this word
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long - need to break it
                    if current_line:
                        wrapped_lines.append(current_line)
                        current_line = ''
                    
                    # Break word into chunks using ANSI-aware slicing
                    word_start = 0
                    while word_start < len(word):
                        # Try to find a good break point (space, punctuation)
                        # For now, just slice by width
                        chunk = slice_ansi(word, word_start, word_start + max_width)
                        if chunk:
                            wrapped_lines.append(chunk)
                            # Calculate how much we consumed
                            chunk_width = string_width(chunk)
                            word_start += chunk_width
                        else:
                            break
            
            if current_line:
                wrapped_lines.append(current_line)
    
    return '\n'.join(wrapped_lines)

def _truncate_text(text: str, max_width: int, truncate_type: str) -> str:
    """
    Truncate text to max width using ANSI-aware operations.
    Matches cli-truncate behavior.
    
    Handles multiline text by truncating each line separately.
    """
    # Handle multiline text
    if '\n' in text:
        lines = text.split('\n')
        truncated_lines = [
            _truncate_text(line, max_width, truncate_type)
            for line in lines
        ]
        return '\n'.join(truncated_lines)
    
    text_width = string_width(text)
    
    if text_width <= max_width:
        return text
    
    ellipsis = '…'
    ellipsis_width = string_width(ellipsis)
    available_width = max_width - ellipsis_width
    
    if available_width < 0:
        # Max width is smaller than ellipsis - just return ellipsis
        return ellipsis
    
    if truncate_type == 'truncate-end':
        # Truncate at end: keep start, add ellipsis
        truncated = slice_ansi(text, 0, available_width) + ellipsis
        # Ensure ANSI codes are properly closed
        truncated = _ensure_ansi_reset(truncated, text)
    elif truncate_type == 'truncate-middle':
        # Truncate in middle: keep start and end, ellipsis in middle
        # Split available width evenly, but ensure we use all available space
        half_width = (available_width + 1) // 2  # Round up for first half
        remaining = available_width - half_width  # Remaining for second half
        
        start_part = slice_ansi(text, 0, half_width)
        end_part = slice_ansi(text, text_width - remaining, text_width)
        truncated = start_part + ellipsis + end_part
        # Ensure ANSI codes are properly closed
        truncated = _ensure_ansi_reset(truncated, text)
    elif truncate_type == 'truncate-start':
        # Truncate at start: ellipsis, then end
        truncated = ellipsis + slice_ansi(text, text_width - available_width, text_width)
        # Ensure ANSI codes are properly closed
        truncated = _ensure_ansi_reset(truncated, text)
    else:
        # Default: truncate at end
        truncated = slice_ansi(text, 0, available_width) + ellipsis
        truncated = _ensure_ansi_reset(truncated, text)
    
    return truncated


def _ensure_ansi_reset(truncated: str, original: str) -> str:
    """
    Ensure ANSI codes are properly closed in truncated text.
    
    If the original text had ANSI codes, ensure the truncated version
    has a reset code at the end if needed.
    """
    # Check if original had ANSI codes
    tokens = tokenize_ansi(original)
    has_ansi = any(token.get('type') == 'ansi' for token in tokens)
    
    if not has_ansi:
        return truncated
    
    # Check if truncated ends with an ANSI code (should end with reset)
    truncated_tokens = tokenize_ansi(truncated)
    
    # If the last token is not a reset code, add one
    if truncated_tokens:
        last_token = truncated_tokens[-1]
        if last_token.get('type') == 'ansi' and last_token.get('value') != '\x1b[0m':
            # Check if we need to add reset
            # Look for any ANSI codes in the truncated text
            has_ansi_in_truncated = any(
                t.get('type') == 'ansi' and t.get('value') != '\x1b[0m'
                for t in truncated_tokens
            )
            if has_ansi_in_truncated:
                # Find the last non-reset ANSI code and ensure reset follows
                # For simplicity, just append reset if not present
                if not truncated.endswith('\x1b[0m'):
                    truncated += '\x1b[0m'
        elif last_token.get('type') != 'ansi':
            # Last token is text - check if we need to add reset
            # Check if there are any open ANSI codes
            has_open_ansi = False
            for token in reversed(truncated_tokens):
                if token.get('type') == 'ansi':
                    if token.get('value') == '\x1b[0m':
                        break  # Found reset, no open codes
                    else:
                        has_open_ansi = True
                        break
            
            if has_open_ansi:
                truncated += '\x1b[0m'
    
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

# Removed _truncate_preserving_ansi - now using slice_ansi from ansi_tokenize

