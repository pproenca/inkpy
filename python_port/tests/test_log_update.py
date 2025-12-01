"""
Tests for log_update module - Terminal output management.

Ported from: src/log-update.ts
"""
import io
import pytest
from inkpy.log_update import create_log_update


def test_log_update_writes_output():
    """Test basic output writing"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log("Hello, World!")
    output = stream.getvalue()
    assert "Hello, World!" in output


def test_log_update_erases_previous():
    """Test that previous output is erased before new output"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log("First")
    log("Second")
    output = stream.getvalue()
    # Should contain erase sequence before "Second"
    assert "\x1b[" in output  # ANSI escape


def test_log_update_clear():
    """Test clearing output"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log("Content")
    log.clear()
    output = stream.getvalue()
    assert "\x1b[" in output  # Erase sequence


def test_log_update_done():
    """Test done() restores cursor"""
    stream = io.StringIO()
    log = create_log_update(stream, show_cursor=False)
    log("Content")
    log.done()
    output = stream.getvalue()
    # Should show cursor at end
    assert "\x1b[?25h" in output  # Show cursor sequence


def test_log_update_hides_cursor():
    """Test cursor is hidden during rendering"""
    stream = io.StringIO()
    log = create_log_update(stream, show_cursor=False)
    log("Content")
    output = stream.getvalue()
    assert "\x1b[?25l" in output  # Hide cursor sequence


def test_incremental_rendering():
    """Test incremental mode only updates changed lines"""
    stream = io.StringIO()
    log = create_log_update(stream, incremental=True)
    log("Line 1\nLine 2\nLine 3")
    log("Line 1\nChanged\nLine 3")
    # Incremental should skip unchanged lines
    output = stream.getvalue()
    # Should contain "Changed" but not rewrite "Line 1" or "Line 3"
    assert "Changed" in output


def test_log_update_sync():
    """Test sync() updates state without writing"""
    stream = io.StringIO()
    log = create_log_update(stream)
    log.sync("Synced content")
    output = stream.getvalue()
    assert output == ""  # Nothing written

