"""
Tests for ANSI escape sequences.

Following TDD: Write failing test first, then implement.
"""

from inkpy.log_update import (
    CURSOR_NEXT_LINE,
    ERASE_LINE,
    clear_terminal,
    cursor_down,
    cursor_left,
    cursor_right,
    cursor_to,
    cursor_up,
    erase_down,
    erase_lines,
    erase_screen,
    erase_up,
)


def test_clear_terminal_exists():
    """Test that clear_terminal function exists"""
    assert clear_terminal is not None
    assert callable(clear_terminal)


def test_clear_terminal_returns_ansi_sequence():
    """Test that clear_terminal returns ANSI escape sequence"""
    result = clear_terminal()
    assert isinstance(result, str)
    assert result.startswith("\x1b[") or result.startswith("\x1b")


def test_cursor_down_exists():
    """Test that cursor_down function exists"""
    assert cursor_down is not None
    assert callable(cursor_down)


def test_cursor_down_moves_down():
    """Test that cursor_down moves cursor down"""
    result = cursor_down(3)
    assert result == "\x1b[3B"


def test_cursor_left_exists():
    """Test that cursor_left function exists"""
    assert cursor_left is not None
    assert callable(cursor_left)


def test_cursor_left_moves_left():
    """Test that cursor_left moves cursor left"""
    result = cursor_left(5)
    assert result == "\x1b[5D"


def test_cursor_right_exists():
    """Test that cursor_right function exists"""
    assert cursor_right is not None
    assert callable(cursor_right)


def test_cursor_right_moves_right():
    """Test that cursor_right moves cursor right"""
    result = cursor_right(2)
    assert result == "\x1b[2C"


def test_cursor_to_exists():
    """Test that cursor_to function exists"""
    assert cursor_to is not None
    assert callable(cursor_to)


def test_cursor_to_moves_to_position():
    """Test that cursor_to moves cursor to specific position"""
    result = cursor_to(10, 5)
    # ANSI format: \x1b[row;colH (both 1-indexed)
    # cursor_to(x, y) = column x, row y -> \x1b[y;xH
    assert result == "\x1b[5;10H"  # row 5, column 10


def test_erase_down_exists():
    """Test that erase_down function exists"""
    assert erase_down is not None
    assert callable(erase_down)


def test_erase_down_erases_down():
    """Test that erase_down erases from cursor down"""
    result = erase_down()
    assert result == "\x1b[J"


def test_erase_up_exists():
    """Test that erase_up function exists"""
    assert erase_up is not None
    assert callable(erase_up)


def test_erase_up_erases_up():
    """Test that erase_up erases from cursor up"""
    result = erase_up()
    assert result == "\x1b[1J"


def test_erase_screen_exists():
    """Test that erase_screen function exists"""
    assert erase_screen is not None
    assert callable(erase_screen)


def test_erase_screen_erases_all():
    """Test that erase_screen erases entire screen"""
    result = erase_screen()
    assert result == "\x1b[2J"


def test_existing_functions_still_work():
    """Test that existing functions still work"""
    assert erase_lines(3) != ""
    assert cursor_up(2) == "\x1b[2A"
    assert ERASE_LINE == "\x1b[2K"
    assert CURSOR_NEXT_LINE == "\x1b[1E"
