"""
App-level hooks for custom reconciler.

Provides use_app and use_input hooks that work with the custom reconciler.
These are simplified versions focused on the core functionality needed
for interactive terminal applications.
"""
from typing import Callable, Optional, Any, Dict
import sys
import tty
import termios
import select
import threading
from inkpy.reconciler.hooks import use_effect, use_context, create_context, Context
from inkpy.input.keypress import Key, parse_keypress, NON_ALPHANUMERIC_KEYS

# App context for exit functionality
AppContext: Context[Dict[str, Any]] = create_context({
    'exit': lambda error=None: None,
})

# Stdin context for input handling  
StdinContext: Context[Dict[str, Any]] = create_context({
    'stdin': sys.stdin,
    'set_raw_mode': lambda mode: None,
    'internal_exitOnCtrlC': True,
})

# Global storage for app state (workaround until full context is implemented)
_app_state = {
    'exit_callback': None,
    'stdin': sys.stdin,
    'raw_mode': False,
    'exit_on_ctrl_c': True,
    'input_handlers': [],
    'input_thread': None,
    'running': False,
}


def set_app_exit_callback(callback: Callable[[Optional[Exception]], None]):
    """Set the app exit callback (called by Ink when using custom reconciler)"""
    _app_state['exit_callback'] = callback


def set_app_stdin(stdin):
    """Set the stdin stream (called by Ink when using custom reconciler)"""
    _app_state['stdin'] = stdin


def set_app_exit_on_ctrl_c(value: bool):
    """Set exit on Ctrl+C behavior"""
    _app_state['exit_on_ctrl_c'] = value


def _start_input_thread():
    """Start background thread for reading input"""
    if _app_state['running']:
        return
    
    _app_state['running'] = True
    
    def read_input():
        stdin = _app_state['stdin']
        fd = stdin.fileno() if hasattr(stdin, 'fileno') else None
        
        if fd is None:
            return
        
        old_settings = None
        try:
            # Enable raw mode
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            _app_state['raw_mode'] = True
            
            while _app_state['running']:
                # Check if input is available (with timeout)
                if select.select([stdin], [], [], 0.1)[0]:
                    data = stdin.read(1)
                    if data:
                        # Read any additional available bytes
                        while select.select([stdin], [], [], 0)[0]:
                            extra = stdin.read(1)
                            if extra:
                                data += extra
                            else:
                                break
                        
                        # Process input
                        _process_input(data)
        except Exception:
            pass
        finally:
            # Restore terminal settings
            if old_settings is not None:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass
            _app_state['raw_mode'] = False
    
    thread = threading.Thread(target=read_input, daemon=True)
    thread.start()
    _app_state['input_thread'] = thread


def _stop_input_thread():
    """Stop the input reading thread"""
    _app_state['running'] = False


def _process_input(data: str):
    """Process input and call handlers"""
    keypress = parse_keypress(data)
    
    # Build Key object
    key = Key(
        name=keypress.name,
        ctrl=keypress.ctrl,
        shift=keypress.shift,
        meta=keypress.meta or keypress.name == 'escape' or keypress.option,
        option=keypress.option,
        sequence=keypress.sequence,
        raw=keypress.raw,
        code=keypress.code
    )
    
    # Determine input string
    input_str = keypress.ctrl and keypress.name or keypress.sequence
    
    # Strip meta prefix if present
    if input_str.startswith('\u001b'):
        input_str = input_str[1:]
    
    # Empty string for non-alphanumeric keys
    if keypress.name in NON_ALPHANUMERIC_KEYS:
        input_str = ''
    
    # Detect shift for uppercase letters
    if len(input_str) == 1 and isinstance(input_str, str) and input_str.isupper():
        key.shift = True
    
    # Handle Ctrl+C
    if input_str == 'c' and key.ctrl:
        if _app_state['exit_on_ctrl_c'] and _app_state['exit_callback']:
            _app_state['exit_callback'](None)
            return
    
    # Call all registered handlers
    for handler in _app_state['input_handlers'][:]:
        try:
            handler(input_str, key)
        except Exception:
            pass


class UseAppResult:
    """Result object from use_app hook"""
    
    def exit(self, error: Optional[Exception] = None):
        """Exit the application"""
        if _app_state['exit_callback']:
            _app_state['exit_callback'](error)


def use_app() -> UseAppResult:
    """
    Hook that provides access to app-level functionality.
    
    Returns:
        Object with 'exit' method to exit the app
    
    Example:
        @component
        def App():
            app = use_app()
            
            def handle_quit():
                app.exit()
            
            return Text("Press 'q' to quit")
    """
    return UseAppResult()


def use_input(
    handler: Callable[[str, Key], None],
    is_active: bool = True
) -> None:
    """
    Hook for handling keyboard input.
    
    Args:
        handler: Callback function (input_str: str, key: Key) -> None
        is_active: Enable/disable input handling
    
    Example:
        @component
        def App():
            selected, set_selected = use_state(0)
            
            def handle_input(input_str, key):
                if key.up_arrow:
                    set_selected(lambda s: max(0, s - 1))
                elif key.down_arrow:
                    set_selected(lambda s: s + 1)
            
            use_input(handle_input)
            return Text(f"Selected: {selected}")
    """
    def setup_input():
        if not is_active:
            return None
        
        # Register handler
        _app_state['input_handlers'].append(handler)
        
        # Start input thread if not running
        _start_input_thread()
        
        # Cleanup function
        def cleanup():
            if handler in _app_state['input_handlers']:
                _app_state['input_handlers'].remove(handler)
        
        return cleanup
    
    use_effect(setup_input, [is_active])

