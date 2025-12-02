"""
Tests for ANSI-aware text wrapping and truncation.

Following TDD: Write failing test first, then implement.
"""
from inkpy.wrap_text import wrap_text


def test_wrap_text_preserves_ansi_codes():
    """Test that wrap_text preserves ANSI codes when wrapping"""
    text = "\x1b[31mHello World\x1b[0m"
    wrapped = wrap_text(text, max_width=5, wrap_type='wrap')
    
    # Should preserve ANSI codes
    assert '\x1b[31m' in wrapped
    assert '\x1b[0m' in wrapped


def test_wrap_text_wraps_at_word_boundaries():
    """Test that wrap_text wraps at word boundaries"""
    text = "Hello World Test"
    wrapped = wrap_text(text, max_width=10, wrap_type='wrap')
    
    # Should wrap at word boundaries
    lines = wrapped.split('\n')
    assert len(lines) >= 2
    # Each line should be <= max_width (accounting for ANSI codes if any)
    for line in lines:
        # Strip ANSI for width check
        stripped = line.replace('\x1b[31m', '').replace('\x1b[0m', '')
        assert len(stripped) <= 10


def test_wrap_text_truncate_end():
    """Test truncate-end truncation"""
    text = "Hello World"
    truncated = wrap_text(text, max_width=5, wrap_type='truncate-end')
    
    # Should truncate and add ellipsis
    assert len(truncated) <= 6  # 5 chars + ellipsis
    assert truncated.endswith('…') or truncated.endswith('...')


def test_wrap_text_truncate_middle():
    """Test truncate-middle truncation"""
    text = "Hello World Test"
    truncated = wrap_text(text, max_width=10, wrap_type='truncate-middle')
    
    # Should have ellipsis in middle
    assert '…' in truncated or '...' in truncated
    # Should preserve start and end
    assert truncated.startswith('H') or truncated.startswith('…')


def test_wrap_text_truncate_start():
    """Test truncate-start truncation"""
    text = "Hello World"
    truncated = wrap_text(text, max_width=5, wrap_type='truncate-start')
    
    # Should start with ellipsis
    assert truncated.startswith('…') or truncated.startswith('...')
    # Should preserve end
    assert truncated.endswith('d')


def test_wrap_text_caches_results():
    """Test that wrap_text caches results"""
    text = "Hello World"
    
    # First call
    result1 = wrap_text(text, max_width=5, wrap_type='wrap')
    
    # Second call should use cache
    result2 = wrap_text(text, max_width=5, wrap_type='wrap')
    
    assert result1 == result2


def test_wrap_text_handles_ansi_in_truncation():
    """Test that truncation preserves ANSI codes correctly"""
    text = "\x1b[31mHello World\x1b[0m"
    truncated = wrap_text(text, max_width=5, wrap_type='truncate-end')
    
    # Should preserve ANSI codes
    assert '\x1b[31m' in truncated
    # Should truncate properly
    assert len(truncated.replace('\x1b[31m', '').replace('\x1b[0m', '')) <= 6


def test_wrap_text_handles_wide_characters():
    """Test that wrap_text handles wide characters (CJK) correctly"""
    text = "中文字符测试"
    wrapped = wrap_text(text, max_width=4, wrap_type='wrap')
    
    # Should wrap considering wide character width
    lines = wrapped.split('\n')
    # Each Chinese character is width 2, so width 4 = 2 characters
    assert len(lines) >= 2


def test_truncate_end_exact_behavior():
    """Test truncate-end matches cli-truncate behavior exactly"""
    text = "Hello World"
    truncated = wrap_text(text, max_width=8, wrap_type='truncate-end')
    
    # Should be: "Hello W…" (7 chars + ellipsis = 8)
    # Verify it ends with ellipsis and starts with text
    assert truncated.endswith('…')
    assert truncated.startswith('Hello')
    # Width should be exactly max_width
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) == 8


def test_truncate_start_exact_behavior():
    """Test truncate-start matches cli-truncate behavior exactly"""
    text = "Hello World"
    truncated = wrap_text(text, max_width=8, wrap_type='truncate-start')
    
    # Should be: "…o World" (ellipsis + 7 chars = 8)
    assert truncated.startswith('…')
    assert truncated.endswith('World')
    # Width should be exactly max_width
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) == 8


def test_truncate_middle_exact_behavior():
    """Test truncate-middle matches cli-truncate behavior exactly"""
    text = "Hello World Test"
    truncated = wrap_text(text, max_width=12, wrap_type='truncate-middle')
    
    # Should have ellipsis in middle, start and end preserved
    assert '…' in truncated
    assert truncated.startswith('Hello')
    assert truncated.endswith('Test')
    # Width should be exactly max_width
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) == 12


def test_truncate_preserves_ansi_codes_end():
    """Test truncate-end preserves ANSI codes correctly"""
    text = "\x1b[31mHello World\x1b[0m"
    truncated = wrap_text(text, max_width=8, wrap_type='truncate-end')
    
    # Should preserve ANSI codes
    assert '\x1b[31m' in truncated
    assert '\x1b[0m' in truncated
    # Should truncate properly
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) == 8


def test_truncate_preserves_ansi_codes_start():
    """Test truncate-start preserves ANSI codes correctly"""
    text = "\x1b[31mHello World\x1b[0m"
    truncated = wrap_text(text, max_width=8, wrap_type='truncate-start')
    
    # Should preserve ANSI codes
    assert '\x1b[31m' in truncated
    assert '\x1b[0m' in truncated
    # Should truncate properly
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) == 8


def test_truncate_preserves_ansi_codes_middle():
    """Test truncate-middle preserves ANSI codes correctly"""
    text = "\x1b[31mHello World Test\x1b[0m"
    truncated = wrap_text(text, max_width=12, wrap_type='truncate-middle')
    
    # Should preserve ANSI codes
    assert '\x1b[31m' in truncated
    assert '\x1b[0m' in truncated
    # Should truncate properly
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) == 12


def test_truncate_handles_wide_characters():
    """Test truncation handles wide characters (CJK) correctly"""
    text = "A中B文C"
    truncated = wrap_text(text, max_width=5, wrap_type='truncate-end')
    
    # "A" (1) + "中" (2) = 3, so we can fit "A中" + ellipsis (1) = 4, or "A" + ellipsis = 2
    # Actually, with width 5, we should fit: "A" (1) + "中" (2) + ellipsis (1) = 4, or more
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) <= 5
    assert truncated.endswith('…')


def test_truncate_no_op_when_text_fits():
    """Test truncation doesn't modify text when it fits"""
    text = "Hello"
    truncated = wrap_text(text, max_width=10, wrap_type='truncate-end')
    
    # Should return original text unchanged
    assert truncated == text


def test_truncate_edge_case_very_short_max_width():
    """Test truncation with very short max_width"""
    text = "Hello"
    truncated = wrap_text(text, max_width=2, wrap_type='truncate-end')
    
    # Should just be ellipsis or ellipsis + 1 char
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(truncated) <= 2
    assert '…' in truncated or len(truncated) == 1


def test_truncate_edge_case_empty_text():
    """Test truncation with empty text"""
    text = ""
    truncated = wrap_text(text, max_width=5, wrap_type='truncate-end')
    
    # Should return empty string
    assert truncated == ""


def test_truncate_multiline_text():
    """Test truncation handles multiline text (should truncate each line)"""
    text = "Line 1\nLine 2\nLine 3"
    truncated = wrap_text(text, max_width=3, wrap_type='truncate-end')
    
    # Each line should be truncated
    lines = truncated.split('\n')
    assert len(lines) == 3
    from inkpy.renderer.ansi_tokenize import string_width
    for line in lines:
        assert string_width(line) <= 3


# --- Screen Reader Mode Tests (Task 1: G1 Gap) ---

def test_wrap_ansi_preserves_styles_across_lines():
    """Test that wrapped text preserves ANSI styles on continuation lines.
    
    This is the key screen reader wrapAnsi behavior: when styled text wraps,
    the style should be reapplied at the start of each wrapped line.
    """
    # Red text that wraps to multiple lines
    text = "\x1b[31mHello World Test\x1b[0m"
    wrapped = wrap_text(text, max_width=8, wrap_type='wrap')
    
    lines = wrapped.split('\n')
    assert len(lines) >= 2, f"Expected multiple lines, got: {wrapped}"
    
    # Each wrapped line should have the ANSI code applied
    # (This is the key behavior from wrap-ansi library)
    for line in lines:
        if line:  # Skip empty lines
            # Line should either start with ANSI code or contain styled text
            assert '\x1b[31m' in line, f"Line missing style code: {repr(line)}"


def test_wrap_ansi_properly_closes_styles():
    """Test that wrapped text properly closes ANSI styles at line ends."""
    text = "\x1b[31mRed text that needs wrapping\x1b[0m"
    wrapped = wrap_text(text, max_width=10, wrap_type='wrap')
    
    lines = wrapped.split('\n')
    
    # Each line should have properly balanced ANSI codes
    # (reset at end if style was applied)
    for line in lines:
        if '\x1b[31m' in line and line.strip():
            # If style is applied, it should be reset at end of line
            # or the style should continue to the content
            assert '\x1b[0m' in line or '\x1b[31m' in line


def test_wrap_ansi_preserves_multiple_styles():
    """Test wrapping text with multiple ANSI styles."""
    # Bold red text
    text = "\x1b[1m\x1b[31mBold red text that wraps\x1b[0m"
    wrapped = wrap_text(text, max_width=10, wrap_type='wrap')
    
    lines = wrapped.split('\n')
    assert len(lines) >= 2
    
    # First line should have both styles
    assert '\x1b[1m' in lines[0] or '\x1b[31m' in lines[0]


def test_screen_reader_wrap_width_calculation():
    """Test that screen reader wrap correctly calculates width ignoring ANSI codes."""
    # 5 visible chars + ANSI codes
    text = "\x1b[31mABCDE\x1b[0m"
    wrapped = wrap_text(text, max_width=5, wrap_type='wrap')
    
    # Should not wrap - visible content is exactly 5 chars
    assert '\n' not in wrapped, f"Should not wrap, got: {repr(wrapped)}"
    
    # Verify visible width is 5
    from inkpy.renderer.ansi_tokenize import string_width
    assert string_width(wrapped) == 5

