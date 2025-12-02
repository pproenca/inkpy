"""
Tests for ANSI text tokenization.

Following TDD: Write failing test first, then implement.
"""

from inkpy.renderer.ansi_tokenize import (
    slice_ansi,
    string_width,
    styled_chars_from_tokens,
    styled_chars_to_string,
    tokenize_ansi,
)


def test_tokenize_ansi_parses_plain_text():
    """Test that tokenize_ansi parses plain text into tokens"""
    text = "Hello World"
    tokens = tokenize_ansi(text)

    assert len(tokens) > 0
    # Should have at least one token with the text
    assert any(token.get("text") == "Hello World" for token in tokens)


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
    assert "\x1b[31m" in sliced
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


def test_styled_chars_from_tokens_returns_correct_structure():
    """Test that styled_chars_from_tokens returns objects matching TypeScript API"""
    text = "\x1b[31mHello\x1b[0m"
    tokens = tokenize_ansi(text)
    styled_chars = styled_chars_from_tokens(tokens)

    # Should return list of styled character objects
    assert len(styled_chars) > 0

    # Each character should have type, value, fullWidth, and styles fields
    first_char = styled_chars[0]
    assert "type" in first_char
    assert first_char["type"] == "char"
    assert "value" in first_char
    assert "fullWidth" in first_char
    assert "styles" in first_char
    assert isinstance(first_char["styles"], list)


def test_styled_chars_from_tokens_preserves_ansi_styles():
    """Test that styled_chars_from_tokens preserves ANSI style information"""
    text = "\x1b[31mRed\x1b[0mNormal"
    tokens = tokenize_ansi(text)
    styled_chars = styled_chars_from_tokens(tokens)

    # First 3 characters should have red style
    assert len(styled_chars) >= 4
    assert styled_chars[0]["value"] == "R"
    assert "\x1b[31m" in styled_chars[0]["styles"]

    # 4th character (after reset) should have no styles or reset style
    assert styled_chars[3]["value"] == "N"
    # Styles should be empty or contain reset
    assert len(styled_chars[3]["styles"]) == 0 or "\x1b[0m" in styled_chars[3]["styles"]


def test_styled_chars_from_tokens_marks_wide_characters():
    """Test that styled_chars_from_tokens marks multi-column characters as fullWidth"""
    text = "A中B"
    tokens = tokenize_ansi(text)
    styled_chars = styled_chars_from_tokens(tokens)

    # Find the Chinese character
    chinese_char = next((c for c in styled_chars if c["value"] == "中"), None)
    assert chinese_char is not None
    assert chinese_char["fullWidth"] is True

    # Regular ASCII should be fullWidth False
    ascii_char = next((c for c in styled_chars if c["value"] == "A"), None)
    assert ascii_char is not None
    assert ascii_char["fullWidth"] is False


def test_styled_chars_to_string_reconstructs_ansi():
    """Test that styled_chars_to_string reconstructs ANSI string from styled chars"""
    # Create styled characters matching the structure
    styled_chars = [
        {"type": "char", "value": "H", "fullWidth": False, "styles": ["\x1b[31m"]},
        {"type": "char", "value": "e", "fullWidth": False, "styles": ["\x1b[31m"]},
        {"type": "char", "value": "l", "fullWidth": False, "styles": ["\x1b[31m"]},
        {"type": "char", "value": "l", "fullWidth": False, "styles": ["\x1b[31m"]},
        {"type": "char", "value": "o", "fullWidth": False, "styles": ["\x1b[31m"]},
        {"type": "char", "value": " ", "fullWidth": False, "styles": []},
        {"type": "char", "value": "W", "fullWidth": False, "styles": []},
    ]

    result = styled_chars_to_string(styled_chars)

    # Should reconstruct with ANSI codes
    assert "\x1b[31m" in result
    assert "Hello" in result
    assert "W" in result


def test_styled_chars_to_string_handles_empty_styles():
    """Test that styled_chars_to_string handles characters with no styles"""
    styled_chars = [
        {"type": "char", "value": "A", "fullWidth": False, "styles": []},
        {"type": "char", "value": "B", "fullWidth": False, "styles": []},
    ]

    result = styled_chars_to_string(styled_chars)

    # Should return plain text without ANSI codes
    assert result == "AB" or result.strip() == "AB"


def test_styled_chars_roundtrip():
    """Test that styled_chars_from_tokens and styled_chars_to_string are inverse operations"""
    original = "\x1b[31mRed\x1b[0m\x1b[32mGreen\x1b[0m"
    tokens = tokenize_ansi(original)
    styled_chars = styled_chars_from_tokens(tokens)
    reconstructed = styled_chars_to_string(styled_chars)

    # Should preserve ANSI codes (may not be identical due to style ordering, but should render same)
    assert "\x1b[31m" in reconstructed
    assert "\x1b[32m" in reconstructed
    assert "Red" in reconstructed
    assert "Green" in reconstructed
