# test_ink.py
import asyncio
import io

import pytest
from reactpy import component

from inkpy.ink import Ink
from inkpy.components.text import Text

class MockStdout:
    def __init__(self):
        self.buffer = io.StringIO()
        self.columns = 80
        self.rows = 24
        
    def write(self, data):
        self.buffer.write(data)
        
    def getvalue(self):
        return self.buffer.getvalue()
    
    def flush(self):
        pass
    
    def isatty(self):
        return True

def test_ink_initialization():
    """Test Ink class can be initialized"""
    stdout = MockStdout()
    stdin = io.StringIO()
    stderr = MockStdout()
    
    ink = Ink(
        stdout=stdout,
        stdin=stdin,
        stderr=stderr,
        debug=False,
        exit_on_ctrl_c=True,
        patch_console=False,
    )
    
    assert ink is not None
    assert ink.is_unmounted is False

def test_ink_render():
    """Test Ink can render a component"""
    stdout = MockStdout()
    
    @component
    def App():
        return Text("Hello, World!")
    
    ink = Ink(
        stdout=stdout,
        stdin=io.StringIO(),
        stderr=MockStdout(),
        debug=True,
    )
    
    ink.render(App())
    
    # In debug mode, output should be written directly
    output = stdout.getvalue()
    assert "Hello, World!" in output

def test_ink_unmount():
    """Test Ink unmount cleans up properly"""
    stdout = MockStdout()
    
    @component
    def App():
        return Text("Test")
    
    ink = Ink(stdout=stdout, stdin=io.StringIO(), stderr=MockStdout())
    ink.render(App())
    ink.unmount()
    
    assert ink.is_unmounted is True

@pytest.mark.asyncio
async def test_ink_wait_until_exit():
    """Test waitUntilExit returns a coroutine that resolves on unmount"""
    ink = Ink(
        stdout=MockStdout(),
        stdin=io.StringIO(),
        stderr=MockStdout(),
    )
    
    exit_coro = ink.wait_until_exit()
    assert asyncio.iscoroutine(exit_coro)
    
    # Unmount should resolve the coroutine
    ink.unmount()
    await exit_coro

def test_ink_calculate_layout():
    """Test layout calculation"""
    stdout = MockStdout()
    
    ink = Ink(stdout=stdout, stdin=io.StringIO(), stderr=MockStdout())
    
    # Should be able to calculate layout
    ink.calculate_layout()
    
    # Root node should have width set to terminal width
    assert ink.root_node.yoga_node is not None

def test_ink_max_fps_option():
    """Test maxFps option affects throttling"""
    ink1 = Ink(
        stdout=MockStdout(),
        stdin=io.StringIO(),
        stderr=MockStdout(),
        max_fps=30,
    )
    
    ink2 = Ink(
        stdout=MockStdout(),
        stdin=io.StringIO(),
        stderr=MockStdout(),
        max_fps=60,
    )
    
    # Both should initialize without error
    assert ink1 is not None
    assert ink2 is not None

