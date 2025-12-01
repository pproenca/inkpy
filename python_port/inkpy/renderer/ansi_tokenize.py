"""
ANSI text tokenization module.

Ports ANSI tokenization functionality for proper text handling with ANSI codes.
Handles parsing ANSI escape sequences, preserving styles during operations,
and calculating character widths (including CJK characters).
"""
import re
from typing import List, Dict, Any, Optional

# Import wcwidth for proper character width calculation
try:
    import wcwidth
    HAS_WCWIDTH = True
except ImportError:
    HAS_WCWIDTH = False
    # Fallback: basic width calculation (doesn't handle CJK properly)
    def _fallback_wcwidth(char: str) -> int:
        """Fallback width calculation - assumes most chars are width 1"""
        # Basic CJK detection (not comprehensive)
        code_point = ord(char)
        # CJK Unified Ideographs range
        if 0x4E00 <= code_point <= 0x9FFF:
            return 2
        # CJK Extension A
        if 0x3400 <= code_point <= 0x4DBF:
            return 2
        # Other wide character ranges
        if code_point in range(0x20000, 0x2A6DF):  # CJK Extension B
            return 2
        return 1


# ANSI escape sequence pattern
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def string_width(text: str) -> int:
    """
    Calculate display width of text, ignoring ANSI codes.
    
    Args:
        text: Text potentially containing ANSI codes
    
    Returns:
        Display width in characters (CJK characters count as 2)
    """
    # Strip ANSI codes first
    stripped = ANSI_ESCAPE_PATTERN.sub('', text)
    
    if HAS_WCWIDTH:
        # Use wcwidth for accurate character width
        width = 0
        for char in stripped:
            width += wcwidth.wcwidth(char)
        return width
    else:
        # Fallback: use basic width calculation
        width = 0
        for char in stripped:
            width += _fallback_wcwidth(char)
        return width


def tokenize_ansi(text: str) -> List[Dict[str, Any]]:
    """
    Tokenize text with ANSI codes into tokens.
    
    Each token represents either:
    - ANSI escape sequence (type: 'ansi')
    - Text content (type: 'text')
    
    Args:
        text: Text with ANSI codes
    
    Returns:
        List of tokens with 'type' and 'value'/'text' fields
    """
    tokens: List[Dict[str, Any]] = []
    i = 0
    
    while i < len(text):
        # Check for ANSI escape sequence
        match = ANSI_ESCAPE_PATTERN.match(text, i)
        if match:
            # Found ANSI code
            tokens.append({
                'type': 'ansi',
                'value': match.group(0)
            })
            i = match.end()
        else:
            # Find next ANSI code or end of string
            next_ansi = ANSI_ESCAPE_PATTERN.search(text, i)
            if next_ansi:
                # Text before ANSI code
                text_part = text[i:next_ansi.start()]
                if text_part:
                    tokens.append({
                        'type': 'text',
                        'text': text_part
                    })
                i = next_ansi.start()
            else:
                # Rest of string is text
                text_part = text[i:]
                if text_part:
                    tokens.append({
                        'type': 'text',
                        'text': text_part
                    })
                break
    
    return tokens


def slice_ansi(text: str, start: int, end: Optional[int] = None) -> str:
    """
    Slice text preserving ANSI codes.
    
    Similar to JavaScript's sliceAnsi, this slices text by display width
    while preserving ANSI escape sequences.
    
    Args:
        text: Text with ANSI codes
        start: Start position (in display width, not character count)
        end: End position (in display width, not character count). If None, slices to end.
    
    Returns:
        Sliced text with ANSI codes preserved
    """
    if end is not None and start >= end:
        return ''
    
    tokens = tokenize_ansi(text)
    result = []
    current_width = 0
    
    for token in tokens:
        if token['type'] == 'ansi':
            # Always include ANSI codes
            result.append(token['value'])
        elif token['type'] == 'text':
            text_content = token['text']
            
            # Calculate how much of this text to include
            text_start = max(0, start - current_width)
            text_end = None if end is None else max(0, end - current_width)
            
            # Calculate character positions based on width
            char_start = 0
            char_end = len(text_content)
            width_so_far = 0
            
            # Find start character position
            for i, char in enumerate(text_content):
                if HAS_WCWIDTH:
                    char_width = wcwidth.wcwidth(char)
                else:
                    char_width = _fallback_wcwidth(char)
                if width_so_far + char_width > text_start:
                    char_start = i
                    break
                width_so_far += char_width
            
            # Find end character position
            if text_end is not None:
                width_so_far = 0
                for i, char in enumerate(text_content[char_start:], char_start):
                    if HAS_WCWIDTH:
                        char_width = wcwidth.wcwidth(char)
                    else:
                        char_width = _fallback_wcwidth(char)
                    if width_so_far >= text_end:
                        char_end = i
                        break
                    width_so_far += char_width
            
            # Add the sliced text
            if char_start < char_end:
                result.append(text_content[char_start:char_end])
            
            current_width += string_width(text_content)
            
            # Stop if we've reached the end
            if end is not None and current_width >= end:
                break
    
    return ''.join(result)


def styled_chars_from_tokens(tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert tokens to styled character list.
    
    Each character includes its ANSI style information.
    
    Args:
        tokens: List of tokens from tokenize_ansi
    
    Returns:
        List of character dictionaries with 'char' and 'style' fields
    """
    styled_chars = []
    current_style = ''
    
    for token in tokens:
        if token['type'] == 'ansi':
            # Update current style
            current_style = token['value']
        elif token['type'] == 'text':
            # Add each character with current style
            for char in token['text']:
                styled_chars.append({
                    'char': char,
                    'style': current_style
                })
    
    return styled_chars


def styled_chars_to_string(styled_chars: List[Dict[str, Any]]) -> str:
    """
    Convert styled character list back to string with ANSI codes.
    
    Args:
        styled_chars: List of character dictionaries
    
    Returns:
        String with ANSI codes inserted appropriately
    """
    result = []
    last_style = None
    
    for char_info in styled_chars:
        char = char_info['char']
        style = char_info.get('style', '')
        
        # Insert ANSI code if style changed
        if style != last_style:
            if last_style is not None:
                # Reset previous style
                result.append('\x1b[0m')
            if style:
                result.append(style)
            last_style = style
        
        result.append(char)
    
    # Reset style at end if needed
    if last_style:
        result.append('\x1b[0m')
    
    return ''.join(result)

