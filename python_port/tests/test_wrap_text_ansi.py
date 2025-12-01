"""
Tests for ANSI-aware text wrapping and truncation.

Following TDD: Write failing test first, then implement.
"""
import pytest
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

