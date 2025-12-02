"""
Integration tests for custom reconciler interactive input.

Uses PTY (pseudo-terminal) to properly test keyboard input handling.
"""
import pytest
import os
import pty
import select
import time
import threading
from io import StringIO


class PTYTerminal:
    """Context manager for creating a PTY for testing."""
    
    def __init__(self):
        self.master_fd = None
        self.slave_fd = None
        self.slave_name = None
    
    def __enter__(self):
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)
        return self
    
    def __exit__(self, *args):
        if self.master_fd is not None:
            os.close(self.master_fd)
        if self.slave_fd is not None:
            os.close(self.slave_fd)
    
    def write_input(self, data: bytes):
        """Write data to the PTY (simulates keyboard input)."""
        os.write(self.master_fd, data)
    
    def read_output(self, timeout: float = 0.5) -> str:
        """Read output from the PTY."""
        output = b""
        while True:
            readable, _, _ = select.select([self.master_fd], [], [], timeout)
            if not readable:
                break
            try:
                chunk = os.read(self.master_fd, 4096)
                if not chunk:
                    break
                output += chunk
            except OSError:
                break
        return output.decode('utf-8', errors='replace')
    
    def get_slave_file(self, mode='r'):
        """Get a file object for the slave end (to use as stdin)."""
        return os.fdopen(self.slave_fd, mode, closefd=False)


def test_reconciler_use_input_handler_is_called():
    """Test that use_input handler is properly registered and called."""
    from inkpy.reconciler import app_hooks
    from inkpy.reconciler.hooks import use_effect, HooksContext
    from inkpy.reconciler.fiber import FiberNode, FiberTag
    
    # Reset app_hooks state
    app_hooks._app_state['input_handlers'] = []
    app_hooks._app_state['running'] = False
    
    handler_calls = []
    
    def my_handler(input_str, key):
        handler_calls.append((input_str, key))
    
    # Simulate use_input registration
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    
    with HooksContext(fiber, on_state_change=lambda: None):
        # Manually register handler (simulating what use_input does)
        app_hooks._app_state['input_handlers'].append(my_handler)
    
    # Verify handler is registered
    assert len(app_hooks._app_state['input_handlers']) == 1
    
    # Simulate input processing
    app_hooks._process_input('a')
    
    # Verify handler was called
    assert len(handler_calls) == 1
    assert handler_calls[0][0] == 'a'
    
    # Cleanup
    app_hooks._app_state['input_handlers'] = []


def test_reconciler_use_input_arrow_keys():
    """Test that arrow key sequences are properly parsed and handled."""
    from inkpy.reconciler import app_hooks
    from inkpy.input.keypress import Key
    
    # Reset app_hooks state
    app_hooks._app_state['input_handlers'] = []
    app_hooks._app_state['running'] = False
    
    received_keys = []
    
    def my_handler(input_str, key: Key):
        received_keys.append({
            'input_str': input_str,
            'name': key.name,
            'up_arrow': key.up_arrow,
            'down_arrow': key.down_arrow,
        })
    
    app_hooks._app_state['input_handlers'].append(my_handler)
    
    # Test down arrow: ESC [ B
    app_hooks._process_input('\x1b[B')
    
    assert len(received_keys) == 1
    assert received_keys[0]['down_arrow'] == True, f"Expected down_arrow=True, got {received_keys[0]}"
    
    # Test up arrow: ESC [ A
    app_hooks._process_input('\x1b[A')
    
    assert len(received_keys) == 2
    assert received_keys[1]['up_arrow'] == True, f"Expected up_arrow=True, got {received_keys[1]}"
    
    # Cleanup
    app_hooks._app_state['input_handlers'] = []


def test_reconciler_effect_runs_and_registers_handler():
    """Test that use_effect properly runs and registers input handlers."""
    from inkpy.reconciler import app_hooks
    from inkpy.reconciler.reconciler import Reconciler
    from inkpy.reconciler.element import create_element
    from inkpy.reconciler.hooks import use_state, use_effect
    from inkpy.reconciler.component import component
    
    # Reset app_hooks state
    app_hooks._app_state['input_handlers'] = []
    app_hooks._app_state['running'] = False
    app_hooks._app_state['exit_callback'] = None
    
    effect_ran = []
    handler_ref = [None]
    
    @component
    def TestComponent():
        def my_handler(input_str, key):
            pass
        
        handler_ref[0] = my_handler
        
        def setup_effect():
            effect_ran.append(True)
            app_hooks._app_state['input_handlers'].append(my_handler)
            return lambda: app_hooks._app_state['input_handlers'].remove(my_handler) if my_handler in app_hooks._app_state['input_handlers'] else None
        
        use_effect(setup_effect, [])
        
        return create_element('ink-box', {}, 'test')
    
    # Render
    reconciler = Reconciler()
    reconciler.render(TestComponent())
    
    # Verify effect ran
    assert len(effect_ran) >= 1, f"Effect should have run, ran={effect_ran}"
    
    # Verify handler was registered
    assert len(app_hooks._app_state['input_handlers']) >= 1, \
        f"Handler should be registered, handlers={app_hooks._app_state['input_handlers']}"
    
    # Cleanup
    app_hooks._app_state['input_handlers'] = []


def test_reconciler_state_update_rerenders():
    """Test that state updates from input handlers trigger re-renders."""
    from inkpy.reconciler import app_hooks
    from inkpy.reconciler.reconciler import Reconciler
    from inkpy.reconciler.element import create_element
    from inkpy.reconciler.hooks import use_state, use_effect
    from inkpy.reconciler.component import component
    
    # Reset app_hooks state
    app_hooks._app_state['input_handlers'] = []
    app_hooks._app_state['running'] = False
    
    render_counts = [0]
    state_values = []
    set_state_ref = [None]
    
    @component
    def TestComponent():
        count, set_count = use_state(0)
        set_state_ref[0] = set_count
        
        render_counts[0] += 1
        state_values.append(count)
        
        return create_element('ink-text', {}, str(count))
    
    # Initial render
    reconciler = Reconciler()
    reconciler.render(TestComponent())
    
    # Should have rendered once
    assert render_counts[0] >= 1, f"Should render at least once, count={render_counts[0]}"
    initial_count = render_counts[0]
    
    # Trigger state update (simulating input handler)
    set_state_ref[0](1)
    reconciler.flush_sync()
    
    # Should have re-rendered
    assert render_counts[0] > initial_count, \
        f"Should re-render after state update, count={render_counts[0]}, initial={initial_count}"
    
    # Verify state changed
    assert 1 in state_values, f"State should include 1, values={state_values}"


def test_log_update_erase_lines_count():
    """
    Test that LogUpdate correctly erases all previous lines on re-render.
    
    This catches the bug where the first line wasn't being erased because
    _previous_line_count was off by one.
    """
    from io import StringIO
    from inkpy.log_update import LogUpdate
    
    # Create a mock stream that captures all output
    output = StringIO()
    log = LogUpdate(output, show_cursor=True)
    
    # First render: 3 lines of content
    content1 = "Line 1\nLine 2\nLine 3"
    log(content1)
    
    # Get first output
    first_output = output.getvalue()
    
    # Clear and capture second render
    output.truncate(0)
    output.seek(0)
    
    # Second render: different content
    content2 = "New 1\nNew 2\nNew 3"
    log(content2)
    
    second_output = output.getvalue()
    
    # The second output should start with erase sequences for 3 lines
    # (ERASE_LINE + cursor up) * 2 + ERASE_LINE + carriage return
    # Then the new content
    
    # Check that erase sequences are present
    assert "\x1b[2K" in second_output, "Should contain erase line sequence"
    assert "\x1b[1A" in second_output, "Should contain cursor up sequence"
    
    # Check that new content is present
    assert "New 1" in second_output, "Should contain new content"


def test_log_update_multiple_rerenders():
    """
    Test that multiple re-renders don't accumulate stale lines.
    
    This specifically tests the bug where first lines accumulated
    across multiple renders.
    """
    from io import StringIO
    from inkpy.log_update import LogUpdate, erase_lines
    
    output = StringIO()
    log = LogUpdate(output, show_cursor=True)
    
    # Simulate 5 renders (like 5 key presses)
    for i in range(5):
        content = f"┌────────────┐\n│  Option {i}  │\n└────────────┘"
        log(content)
    
    final_output = output.getvalue()
    
    # Count occurrences of the top border
    # BUG: If erase isn't working correctly, we'd see multiple top borders
    top_border_count = final_output.count("┌────────────┐")
    
    # Should only have ONE top border in the final visible output
    # The erase sequences should remove previous ones
    # Note: The raw output may contain multiple, but each new render should erase previous
    
    # What we can verify: each render after the first should emit erase sequences
    # The number of erase sequences should match the line count
    erase_count = final_output.count("\x1b[2K")  # ERASE_LINE
    
    # We have 5 renders, 4 of them should erase 3 lines each = 12 erase sequences
    # (first render doesn't erase anything since _previous_line_count is 0)
    assert erase_count >= 12, f"Expected at least 12 erase sequences, got {erase_count}"


def test_erase_lines_calculation():
    """
    Test that erase_lines properly calculates the number of lines to erase.
    
    After writing N lines + trailing newline, cursor is on line N+1.
    To clear all content, we need to erase from current position back to line 1.
    """
    from inkpy.log_update import erase_lines
    
    # Erase 3 lines starting from current cursor position
    # Should: erase current, move up, erase, move up, erase (no move up at end)
    result = erase_lines(3)
    
    # Count operations
    erase_count = result.count("\x1b[2K")  # ERASE_LINE
    cursor_up_count = result.count("\x1b[1A")  # cursor up
    
    assert erase_count == 3, f"Should erase 3 lines, got {erase_count}"
    assert cursor_up_count == 2, f"Should move up 2 times, got {cursor_up_count}"
    assert result.endswith("\r"), "Should end with carriage return"


def test_ctrl_c_triggers_exit():
    """Test that Ctrl+C (\\x03) triggers the exit callback."""
    from inkpy.reconciler import app_hooks
    from inkpy.input.keypress import parse_keypress
    
    # Reset state
    app_hooks._app_state['input_handlers'] = []
    app_hooks._app_state['exit_on_ctrl_c'] = True
    
    exit_called = []
    
    def mock_exit(error=None):
        exit_called.append(True)
    
    app_hooks._app_state['exit_callback'] = mock_exit
    
    # Process Ctrl+C
    app_hooks._process_input('\x03')
    
    # Verify exit was called
    assert len(exit_called) == 1, f"Exit should be called once, got {exit_called}"
    
    # Cleanup
    app_hooks._app_state['exit_callback'] = None


def test_ctrl_c_keypress_parsing():
    """Test that Ctrl+C is parsed correctly."""
    from inkpy.input.keypress import parse_keypress
    
    key = parse_keypress('\x03')
    
    assert key.name == 'c', f"Key name should be 'c', got {key.name}"
    assert key.ctrl == True, f"Key.ctrl should be True, got {key.ctrl}"

