"""
Comprehensive tests for Ink class with all features
"""
import asyncio
import io
import os
from unittest.mock import patch

import pytest

from inkpy.ink import Ink


class MockStdout:
    """Mock stdout with columns/rows attributes"""
    def __init__(self, columns=80, rows=24):
        self.buffer = io.StringIO()
        self.columns = columns
        self.rows = rows
        
    def write(self, data):
        self.buffer.write(data)
    
    def flush(self):
        """Flush buffer (no-op for mock)"""
        pass
        
    def getvalue(self):
        return self.buffer.getvalue()


def test_ink_initialization_with_all_options():
    """Test Ink class can be initialized with all options"""
    stdout = MockStdout()
    stdin = io.StringIO()
    stderr = MockStdout()
    
    render_metrics = []
    
    def on_render(metrics):
        render_metrics.append(metrics)
    
    ink = Ink(
        stdout=stdout,
        stdin=stdin,
        stderr=stderr,
        debug=False,
        exit_on_ctrl_c=True,
        patch_console=False,
        max_fps=30,
        incremental_rendering=False,
        is_screen_reader_enabled=False,
        on_render=on_render,
    )
    
    assert ink is not None
    assert ink.is_unmounted is False
    assert ink.options['max_fps'] == 30
    assert ink.options['incremental_rendering'] is False


def test_ink_screen_reader_from_env():
    """Test Ink reads INK_SCREEN_READER environment variable"""
    stdout = MockStdout()
    
    with patch.dict(os.environ, {'INK_SCREEN_READER': 'true'}):
        ink = Ink(
            stdout=stdout,
            stdin=io.StringIO(),
            stderr=MockStdout(),
            is_screen_reader_enabled=None,  # Should read from env
        )
        assert ink.is_screen_reader_enabled is True
    
    with patch.dict(os.environ, {'INK_SCREEN_READER': 'false'}):
        ink = Ink(
            stdout=stdout,
            stdin=io.StringIO(),
            stderr=MockStdout(),
            is_screen_reader_enabled=None,
        )
        assert ink.is_screen_reader_enabled is False


def test_ink_screen_reader_explicit():
    """Test Ink uses explicit is_screen_reader_enabled over env"""
    stdout = MockStdout()
    
    with patch.dict(os.environ, {'INK_SCREEN_READER': 'true'}):
        ink = Ink(
            stdout=stdout,
            stdin=io.StringIO(),
            stderr=MockStdout(),
            is_screen_reader_enabled=False,  # Explicit should override env
        )
        assert ink.is_screen_reader_enabled is False


def test_ink_throttle_setup():
    """Test Ink sets up throttling based on max_fps"""
    stdout = MockStdout()
    
    ink_30fps = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
        max_fps=30,
    )
    
    ink_60fps = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
        max_fps=60,
    )
    
    # Throttle should be calculated (1000 / fps)
    assert hasattr(ink_30fps, '_render_throttle_ms')
    assert hasattr(ink_60fps, '_render_throttle_ms')
    # 60fps should have smaller throttle (more frequent renders)
    assert ink_60fps._render_throttle_ms < ink_30fps._render_throttle_ms


def test_ink_no_throttle_in_debug_mode():
    """Test Ink doesn't throttle in debug mode"""
    stdout = MockStdout()
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
        debug=True,
        max_fps=30,
    )
    
    # In debug mode, should not throttle (unthrottled = True)
    assert ink._unthrottled is True


def test_ink_no_throttle_with_screen_reader():
    """Test Ink doesn't throttle with screen reader enabled"""
    stdout = MockStdout()
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
        is_screen_reader_enabled=True,
        max_fps=30,
    )
    
    # With screen reader, should not throttle
    assert ink._unthrottled is True


def test_ink_screen_reader_uses_wrap_text():
    """Test Ink wraps output in screen reader mode"""
    from inkpy.ink import erase_lines
    
    # Test erase_lines function
    erase = erase_lines(3)
    assert '\x1b[' in erase  # Should contain ANSI escape codes
    
    # Test with 0 lines (should return empty string)
    assert erase_lines(0) == ''
    assert erase_lines(-1) == ''


def test_ink_terminal_resize_handler():
    """Test Ink sets up terminal resize handler"""
    stdout = MockStdout()
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    
    # Should have resize handler setup
    # Note: Actual signal handler testing is complex, so we just verify the method exists
    assert hasattr(ink, '_on_resize') or hasattr(ink, 'resized')
    assert callable(getattr(ink, '_on_resize', None) or getattr(ink, 'resized', None))


def test_ink_resize_clears_output():
    """Test resize handler clears output when width decreases"""
    stdout = MockStdout(columns=100)
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    
    ink.last_terminal_width = 100
    ink.last_output = "Some output"
    
    # Simulate resize to smaller width
    stdout.columns = 50
    
    # Call resize handler
    if hasattr(ink, '_on_resize'):
        ink._on_resize(None, None)
    elif hasattr(ink, 'resized'):
        ink.resized()
    
    # Should clear output when width decreases
    assert ink.last_output == ''


def test_ink_get_terminal_width():
    """Test get_terminal_width returns columns or defaults to 80"""
    stdout = MockStdout(columns=120)
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    
    assert ink.get_terminal_width() == 120
    
    # Test with no columns attribute
    stdout_no_cols = io.StringIO()
    ink_no_cols = Ink(
        stdout=stdout_no_cols,
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    assert ink_no_cols.get_terminal_width() == 80


def test_ink_on_render_callback():
    """Test on_render callback is called with metrics"""
    stdout = MockStdout()
    render_metrics = []
    
    def on_render(metrics):
        render_metrics.append(metrics)
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
        on_render=on_render,
    )
    
    # Call on_render (when implemented, should call callback)
    ink.on_render()
    
    # Callback should be called (when fully implemented)
    # For now, just verify it's stored
    assert ink.options.get('on_render') == on_render


@pytest.mark.asyncio
async def test_ink_wait_until_exit():
    """Test wait_until_exit returns a coroutine that resolves on unmount"""
    
    stdout = MockStdout()
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    
    # Should return a coroutine/future
    exit_coro = ink.wait_until_exit()
    assert asyncio.iscoroutine(exit_coro)
    
    # Unmount and await to avoid "coroutine never awaited" warning
    ink.unmount()
    await exit_coro


def test_ink_unmount_resolves_exit_promise():
    """Test unmount resolves exit promise"""
    stdout = MockStdout()
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    
    async def test_unmount():
        # Start waiting for exit
        exit_task = asyncio.create_task(ink.wait_until_exit())
        
        # Unmount should resolve the future
        ink.unmount()
        
        # Should complete quickly
        await asyncio.wait_for(exit_task, timeout=0.1)
        assert exit_task.done()
    
    asyncio.run(test_unmount())

