"""
Tests for complete ANSI escape sequence support.

Following TDD: Write failing test first, then implement.
"""
from inkpy.renderer.ansi_tokenize import tokenize_ansi, string_width, slice_ansi


def test_ansi_sgr_sequences():
    """Test SGR (Select Graphic Rendition) sequences"""
    # Common color codes
    text = "\x1b[31mRed\x1b[0m \x1b[32mGreen\x1b[0m \x1b[34mBlue\x1b[0m"
    tokens = tokenize_ansi(text)
    
    # Should parse all ANSI codes
    assert len(tokens) > 0
    assert string_width(text) == string_width("Red Green Blue")


def test_ansi_multiple_parameters():
    """Test ANSI sequences with multiple parameters"""
    text = "\x1b[1;31;42mBold Red on Green\x1b[0m"
    tokens = tokenize_ansi(text)
    
    # Should parse multi-parameter sequences
    assert len(tokens) > 0
    assert string_width(text) == string_width("Bold Red on Green")


def test_ansi_cursor_sequences():
    """Test cursor movement sequences"""
    # Cursor up, down, forward, back
    text = "\x1b[A\x1b[B\x1b[C\x1b[D"
    tokens = tokenize_ansi(text)
    
    # Should parse cursor sequences
    assert len(tokens) > 0


def test_ansi_erase_sequences():
    """Test erase sequences"""
    # Erase in line, erase in display
    text = "\x1b[K\x1b[J"
    tokens = tokenize_ansi(text)
    
    # Should parse erase sequences
    assert len(tokens) > 0


def test_ansi_single_char_sequences():
    """Test single character escape sequences"""
    # ESC + single char (like ESC[ for CSI)
    text = "\x1b[@\x1b[Z"
    tokens = tokenize_ansi(text)
    
    # Should parse single char sequences
    assert len(tokens) > 0


def test_ansi_complex_sequences():
    """Test complex ANSI sequences"""
    # Complex sequence with parameters
    text = "\x1b[38;5;196m256 Color\x1b[0m"
    tokens = tokenize_ansi(text)
    
    # Should parse complex sequences
    assert len(tokens) > 0
    assert string_width(text) == string_width("256 Color")


def test_ansi_preserves_all_sequences():
    """Test that all ANSI sequences are preserved during operations"""
    text = "\x1b[31mRed\x1b[0m \x1b[1mBold\x1b[0m"
    
    # Slice should preserve ANSI codes
    sliced = slice_ansi(text, 0, 3)
    assert '\x1b[31m' in sliced or '\x1b[0m' in sliced
    
    # Width calculation should ignore ANSI codes
    assert string_width(text) == string_width("Red Bold")


def test_ansi_edge_cases():
    """Test edge cases in ANSI sequences"""
    # Empty sequence
    text = "\x1b[m"
    tokens = tokenize_ansi(text)
    assert len(tokens) > 0
    
    # Sequence with no parameters
    text = "\x1b[H"
    tokens = tokenize_ansi(text)
    assert len(tokens) > 0
    
    # Sequence with spaces
    text = "\x1b[ 1 ; 2 m"
    tokens = tokenize_ansi(text)
    assert len(tokens) > 0


def test_ansi_unicode_with_ansi():
    """Test ANSI sequences with Unicode characters"""
    text = "\x1b[31m中\x1b[0m文"
    tokens = tokenize_ansi(text)
    
    # Should handle Unicode + ANSI
    assert len(tokens) > 0
    # Width should account for wide characters (中 is 2, 文 is 2, total 4)
    assert string_width(text) == 4


def test_ansi_nested_sequences():
    """Test nested ANSI sequences"""
    text = "\x1b[31mRed\x1b[1mBold Red\x1b[0mNormal"
    tokens = tokenize_ansi(text)
    
    # Should parse nested sequences
    assert len(tokens) > 0
    assert string_width(text) == string_width("RedBold RedNormal")

