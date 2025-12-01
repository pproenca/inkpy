"""
App component - Root wrapper component for InkPy applications
"""
import sys
import threading
import select
import termios
import tty
from typing import Optional, TextIO, Callable, Dict, Any, List
from reactpy import component, html, use_state, use_effect
from reactpy.core.hooks import use_context
from inkpy.components.app_context import AppContext
from inkpy.components.stdin_context import StdinContext
from inkpy.components.stdout_context import StdoutContext
from inkpy.components.stderr_context import StderrContext
from inkpy.components.focus_context import FocusContext
from inkpy.components.error_overview import ErrorOverview
from inkpy.input.event_emitter import EventEmitter

@component
def App(
    children,
    stdin: TextIO,
    stdout: TextIO,
    stderr: TextIO,
    write_to_stdout: Callable[[str], None],
    write_to_stderr: Callable[[str], None],
    exit_on_ctrl_c: bool = True,
    on_exit: Optional[Callable[[Optional[Exception]], None]] = None,
):
    """
    Root App component that provides all contexts and handles focus/input.
    """
    # Event emitter for input distribution (created once, persisted)
    # Use a list to hold the emitter so it persists across renders
    emitter_container, _ = use_state(lambda: [EventEmitter()])
    event_emitter = emitter_container[0]
    
    # Raw mode reference counting
    raw_mode_count, set_raw_mode_count = use_state(0)
    
    # Input loop thread control - use threading.Event for proper synchronization
    loop_control, _ = use_state(lambda: {'event': threading.Event(), 'thread': None})
    
    # Error boundary state
    error, set_error = use_state(None)
    
    # Handle error - call on_exit when error occurs
    def handle_error_catch(err: Exception):
        """Handle caught error - set state and call on_exit"""
        set_error(err)
        if on_exit:
            on_exit(err)
    
    # Effect to catch errors (ReactPy doesn't have componentDidCatch, so we use effect)
    def setup_error_boundary():
        """Set up error boundary - catch errors during render"""
        # In ReactPy, we need to wrap children rendering in try/except
        # This will be done in the render function
        return None
    
    use_effect(setup_error_boundary, dependencies=[])
    
    # Focus state management
    is_focus_enabled, set_is_focus_enabled = use_state(True)
    active_focus_id, set_active_focus_id = use_state(None)
    focusables, set_focusables = use_state([])
    
    # Check if raw mode is supported
    def is_raw_mode_supported() -> bool:
        """Check if stdin supports raw mode (TTY check)"""
        return stdin.isatty() if hasattr(stdin, 'isatty') else False
    
    # Raw mode management with reference counting
    def handle_set_raw_mode(is_enabled: bool):
        """Enable/disable raw mode with reference counting"""
        if not is_raw_mode_supported():
            if stdin == sys.stdin:
                raise RuntimeError(
                    'Raw mode is not supported on the current process.stdin, which Ink uses as input stream by default.\n'
                    'Read about how to prevent this error on https://github.com/vadimdemedes/ink/#israwmodesupported'
                )
            else:
                raise RuntimeError(
                    'Raw mode is not supported on the stdin provided to Ink.\n'
                    'Read about how to prevent this error on https://github.com/vadimdemedes/ink/#israwmodesupported'
                )
        
        if is_enabled:
            # Increment reference count
            def update_count(current):
                new_count = current + 1
                # Start input loop on first enable
                if new_count == 1:
                    _start_input_loop()
                return new_count
            set_raw_mode_count(update_count)
        else:
            # Decrement reference count
            def update_count(current):
                new_count = max(0, current - 1)
                # Stop input loop when count reaches 0
                if new_count == 0:
                    _stop_input_loop()
                return new_count
            set_raw_mode_count(update_count)
    
    # Input handling
    def handle_input(input_str: str):
        """Handle keyboard input (Tab, Escape, Ctrl+C)"""
        # Exit on Ctrl+C
        if input_str == '\x03' and exit_on_ctrl_c:
            if on_exit:
                on_exit(None)
            return
        
        # Reset focus on Escape
        if input_str == '\x1b' and active_focus_id is not None:
            set_active_focus_id(None)
            return
        
        # Focus navigation
        if is_focus_enabled and focusables:
            if input_str == '\t':
                focus_next()
            elif input_str == '\x1b[Z':  # Shift+Tab
                focus_previous()
    
    # Input reading loop
    def _start_input_loop():
        """Start background thread to read stdin and emit events"""
        if loop_control['thread'] is not None and loop_control['thread'].is_alive():
            return
        
        # Clear the event to start the loop
        loop_control['event'].clear()
        
        def input_loop():
            """Background thread function to read stdin"""
            old_settings = None
            try:
                if is_raw_mode_supported() and hasattr(stdin, 'fileno'):
                    fd = stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    tty.setraw(fd)
                
                # Loop until event is set (stop signal)
                while not loop_control['event'].is_set():
                    # Check if data is available (non-blocking)
                    if hasattr(stdin, 'fileno'):
                        fd = stdin.fileno()
                        ready, _, _ = select.select([fd], [], [], 0.1)
                        if ready:
                            chunk = stdin.read(1)
                            if chunk:
                                handle_input(chunk)
                                event_emitter.emit('input', chunk)
                    else:
                        # Fallback: blocking read with timeout
                        # Use event.wait with timeout instead
                        if loop_control['event'].wait(0.1):
                            break
                        # Try to read if available
                        if hasattr(stdin, 'read'):
                            try:
                                chunk = stdin.read(1) if select.select([stdin], [], [], 0)[0] else None
                                if chunk:
                                    handle_input(chunk)
                                    event_emitter.emit('input', chunk)
                            except Exception:
                                break
            except Exception:
                # Silently handle errors (e.g., stdin closed)
                pass
            finally:
                # Restore terminal settings
                if old_settings is not None and hasattr(stdin, 'fileno'):
                    try:
                        termios.tcsetattr(stdin.fileno(), termios.TCSADRAIN, old_settings)
                    except Exception:
                        pass
        
        thread = threading.Thread(target=input_loop, daemon=True)
        thread.start()
        loop_control['thread'] = thread
    
    def _stop_input_loop():
        """Stop the input reading loop"""
        loop_control['event'].set()
        # Wait a bit for thread to finish (non-blocking)
        if loop_control['thread'] is not None:
            loop_control['thread'].join(timeout=0.1)
    
    # Cleanup on unmount
    def cleanup():
        """Cleanup function called on component unmount"""
        if raw_mode_count > 0:
            _stop_input_loop()
            set_raw_mode_count(0)
    
    use_effect(lambda: cleanup, dependencies=[])
    
    # Focus management functions
    def add_focusable(id: str, options: Dict[str, Any]):
        def update_focusables(current):
            new_list = list(current)
            # Check if already exists
            for i, f in enumerate(new_list):
                if f['id'] == id:
                    new_list[i] = {'id': id, 'is_active': True, **options}
                    return new_list
            new_list.append({'id': id, 'is_active': True, **options})
            # Auto-focus if enabled and no active focus
            if options.get('auto_focus') and active_focus_id is None:
                set_active_focus_id(id)
            return new_list
        set_focusables(update_focusables)
    
    def remove_focusable(id: str):
        def update_focusables(current):
            new_list = [f for f in current if f['id'] != id]
            if active_focus_id == id:
                set_active_focus_id(None)
            return new_list
        set_focusables(update_focusables)
    
    def activate_focus(id: str):
        set_active_focus_id(id)
    
    def deactivate_focus(id: str):
        if active_focus_id == id:
            set_active_focus_id(None)
    
    def enable_focus():
        set_is_focus_enabled(True)
    
    def disable_focus():
        set_is_focus_enabled(False)
        set_active_focus_id(None)
    
    def focus_next():
        if not focusables:
            return
        current_index = next((i for i, f in enumerate(focusables) if f['id'] == active_focus_id), -1)
        next_index = (current_index + 1) % len(focusables)
        set_active_focus_id(focusables[next_index]['id'])
    
    def focus_previous():
        if not focusables:
            return
        current_index = next((i for i, f in enumerate(focusables) if f['id'] == active_focus_id), -1)
        prev_index = (current_index - 1) % len(focusables)
        set_active_focus_id(focusables[prev_index]['id'])
    
    def focus(id: str):
        if any(f['id'] == id for f in focusables):
            set_active_focus_id(id)
        elif focusables:
            set_active_focus_id(focusables[0]['id'])
    
    # Context values
    app_context_value = {
        'exit': lambda error=None: on_exit(error) if on_exit else None
    }
    
    stdin_context_value = {
        'stdin': stdin,
        'set_raw_mode': handle_set_raw_mode,
        'is_raw_mode_supported': is_raw_mode_supported(),
        'internal_exitOnCtrlC': exit_on_ctrl_c,
        'internal_eventEmitter': event_emitter,
    }
    
    stdout_context_value = {
        'stdout': stdout,
        'write': write_to_stdout
    }
    
    stderr_context_value = {
        'stderr': stderr,
        'write': write_to_stderr
    }
    
    focus_context_value = {
        'active_id': active_focus_id,
        'add': add_focusable,
        'remove': remove_focusable,
        'activate': activate_focus,
        'deactivate': deactivate_focus,
        'enable_focus': enable_focus,
        'disable_focus': disable_focus,
        'focus_next': focus_next,
        'focus_previous': focus_previous,
        'focus': focus,
    }
    
    # Provide all contexts - ReactPy contexts use positional children argument
    # Build from innermost to outermost
    inner_content = ErrorOverview(error) if error else children
    
    return html.div(
        AppContext(
            StdinContext(
                StdoutContext(
                    StderrContext(
                        FocusContext(
                            inner_content,
                            value=focus_context_value
                        ),
                        value=stderr_context_value
                    ),
                    value=stdout_context_value
                ),
                value=stdin_context_value
            ),
            value=app_context_value
        )
    )

