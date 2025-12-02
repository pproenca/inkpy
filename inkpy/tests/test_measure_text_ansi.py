# tests/test_measure_text_ansi.py
"""Tests for ANSI-aware text measurement."""
from inkpy.measure_text import measure_text


def test_measure_text_with_ansi_codes():
    """Measure text should correctly measure text with ANSI codes."""
    # Text with ANSI color codes
    text = "\x1b[31mred\x1b[0m"
    result = measure_text(text)
    
    # Should measure visible width (3 chars), not ANSI codes
    assert result['width'] == 3
    assert result['height'] == 1


def test_measure_text_cjk_characters():
    """Measure text should count CJK characters as double width."""
    text = "hello世界"  # 5 + 2*2 = 9 display width
    result = measure_text(text)
    
    # CJK characters are double-width
    assert result['width'] == 9


def test_measure_text_emoji():
    """Measure text should handle emoji width correctly."""
    text = "hi👋"  # 2 + 2 = 4 (emoji is typically 2 wide)
    result = measure_text(text)
    
    # Emoji is typically double-width
    assert result['width'] >= 4


def test_measure_multiline_widest():
    """Measure text should return widest line width."""
    text = "short\nlonger line\nmed"
    result = measure_text(text)
    
    assert result['width'] == 11  # "longer line" length
    assert result['height'] == 3

