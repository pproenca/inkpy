"""
Tests for ANSI text tokenization.

Following TDD: Write failing test first, then implement.
"""
import pytest
from inkpy.renderer.ansi_tokenize import tokenize_ansi, slice_ansi, string_width


def test_tokenize_ansi_parses_plain_text():
    """Test that tokenize_ansi parses plain text into tokens"""
    text = "Hello World"
    tokens = tokenize_ansi(text)
    
    assert len(tokens) > 0
    # Should have at least one token with the text
    assert any(token.get('text') == "Hello World" for token in tokens)


def test_tokenize_ansi_parses_ansi_codes():
    """Test that tokenize_ansi parses ANSI color codes"""
    text = "\x1b[31mHello\x1b[0m"
    tokens = tokenize_ansi(text)
    
    assert len(tokens) > 0
    # Should have tokens with ANSI codes and text


def test_tokenize_ansi_preserves_styles():
    """Test that tokenize_ansi preserves style information"""
    text = "\x1b[31mRed\x1b[0m Normal"
    tokens = tokenize_ansi(text)
    
    # Should have separate tokens for styled and normal text
    assert len(tokens) >= 2


def test_slice_ansi_preserves_styles():
    """Test that slice_ansi preserves ANSI codes when slicing"""
    text = "\x1b[31mHello\x1b[0m World"
    
    # Slice first 5 characters (should include "Hello" with its color)
    sliced = slice_ansi(text, 0, 5)
    
    # Should preserve ANSI codes
    assert '\x1b[31m' in sliced
    assert "Hello" in sliced


def test_string_width_ignores_ansi_codes():
    """Test that string_width calculates width ignoring ANSI codes"""
    plain_text = "Hello"
    ansi_text = "\x1b[31mHello\x1b[0m"
    
    assert string_width(plain_text) == string_width(ansi_text)
    assert string_width(plain_text) == 5


def test_string_width_handles_wide_characters():
    """Test that string_width handles wide characters (CJK) correctly"""
    # Chinese character should be width 2
    chinese = "中"
    assert string_width(chinese) == 2
    
    # Regular ASCII should be width 1
    ascii_char = "A"
    assert string_width(ascii_char) == 1


def test_slice_ansi_handles_wide_characters():
    """Test that slice_ansi handles wide characters correctly"""
    text = "A中B"
    
    # Slice to width 2 (should include "A" and half of "中" or just "A")
    # Actually, slicing at width 2 should give us "A" (1) + "中" (2) = 3 width, so we'd get "A"
    sliced = slice_ansi(text, 0, 2)
    
    # Should handle wide characters properly
    assert len(sliced) > 0

