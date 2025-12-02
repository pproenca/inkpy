from inkpy.renderer.colorize import colorize


def test_foreground_color():
    """Test foreground color application"""
    result = colorize("Hello", "red", "foreground")
    assert "\x1b[31m" in result  # Red ANSI code
    assert "Hello" in result


def test_background_color():
    """Test background color application"""
    result = colorize("Hello", "blue", "background")
    assert "\x1b[44m" in result  # Blue background ANSI code
    assert "Hello" in result


def test_hex_color():
    """Test hex color support"""
    result = colorize("Hello", "#ff0000", "foreground")
    # Should use 24-bit color escape sequence: \x1b[38;2;R;G;Bm
    assert "\x1b[38;2" in result or "\x1b[31m" in result  # Either 24-bit or fallback to red
    assert "Hello" in result


def test_named_colors():
    """Test various named colors"""
    colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"]
    for color in colors:
        result = colorize("Test", color, "foreground")
        assert "Test" in result
        assert "\x1b[" in result  # Should contain ANSI code


def test_256_color_palette():
    """Test 256-color palette support"""
    result = colorize("Hello", 196, "foreground")  # Bright red in 256-color palette
    assert "\x1b[38;5;196m" in result or "\x1b[31m" in result
    assert "Hello" in result


def test_invalid_color():
    """Test that invalid colors don't crash"""
    result = colorize("Hello", "invalid_color", "foreground")
    assert "Hello" in result  # Should still return text


def test_empty_string():
    """Test empty string handling"""
    result = colorize("", "red", "foreground")
    assert result == ""


def test_color_reset():
    """Test that color codes are properly closed"""
    result = colorize("Hello", "red", "foreground")
    # Should end with reset code or have reset somewhere
    assert "\x1b[0m" in result or result.endswith("\x1b[0m")

