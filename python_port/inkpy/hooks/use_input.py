"""
useInput hook module.

Ports use-input functionality from Ink.
Provides a hook for handling user input in ReactPy components.
"""
from typing import Callable, Optional
from reactpy import use_effect
from .use_stdin import use_stdin
from ..input.keypress import Key, parse_keypress, NON_ALPHANUMERIC_KEYS


def use_input(
    input_handler: Callable[[str, Key], None],
    is_active: bool = True
) -> None:
    """
    Hook for handling user input.
    
    This hook is used for handling user input. It's a more convenient
    alternative to using StdinContext and listening for data events.
    The callback you pass to useInput is called for each character when
    the user enters any input. However, if the user pastes text and it's
    more than one character, the callback will be called only once, and
    the whole string will be passed as input.
    
    Args:
        input_handler: Callback function called with (input_str, key) for each input
        is_active: Enable or disable capturing of user input (default: True)
    
    Example:
        @component
        def App():
            def handle_input(input_str: str, key: Key):
                if input_str == 'q':
                    exit()
                if key.upArrow:
                    # Handle up arrow
                    pass
            
            use_input(handle_input)
            return Text("Press 'q' to quit")
    """
    stdin_ctx = use_stdin()
    
    # Set up raw mode when active
    def setup_raw_mode():
        if not is_active:
            return None
        # Access context as dict
        set_raw_mode = stdin_ctx.get('set_raw_mode') if isinstance(stdin_ctx, dict) else getattr(stdin_ctx, 'set_raw_mode', None)
        if set_raw_mode:
            set_raw_mode(True)
            return lambda: set_raw_mode(False)
        return None
    
    use_effect(setup_raw_mode, dependencies=[is_active])
    
    # Set up input listener when active
    def setup_listener():
        if not is_active:
            return None
        return _setup_input_listener(stdin_ctx, input_handler)
    
    use_effect(setup_listener, dependencies=[is_active, input_handler])


def _setup_input_listener(stdin_ctx, input_handler: Callable[[str, Key], None]):
    """Set up input event listener and return cleanup function"""
    def handle_data(data: str):
        """Handle incoming input data"""
        keypress = parse_keypress(data)
        
        # Build Key object matching Ink's Key type
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
        
        # Strip meta prefix if present (for backward compatibility)
        if input_str.startswith('\u001b'):
            input_str = input_str[1:]
        
        # Empty string for non-alphanumeric keys
        if keypress.name in NON_ALPHANUMERIC_KEYS:
            input_str = ''
        
        # Detect shift for uppercase letters
        if len(input_str) == 1 and isinstance(input_str, str) and input_str.isupper():
            key.shift = True
        
        # Call handler (skip if Ctrl+C and exitOnCtrlC is enabled)
        # Access context as dict
        if isinstance(stdin_ctx, dict):
            internal_exit_on_ctrl_c = stdin_ctx.get('internal_exitOnCtrlC', True)
        else:
            internal_exit_on_ctrl_c = getattr(stdin_ctx, 'internal_exitOnCtrlC', True)
        
        if not (input_str == 'c' and key.ctrl) or not internal_exit_on_ctrl_c:
            input_handler(input_str, key)
    
    # Set up event listener if event emitter is available
    # Access context as dict
    if isinstance(stdin_ctx, dict):
        event_emitter = stdin_ctx.get('internal_eventEmitter')
    else:
        event_emitter = getattr(stdin_ctx, 'internal_eventEmitter', None)
    
    if event_emitter:
        if hasattr(event_emitter, 'on'):
            event_emitter.on('input', handle_data)
            return lambda: event_emitter.removeListener('input', handle_data) if hasattr(event_emitter, 'removeListener') else None
        elif hasattr(event_emitter, 'add_listener'):
            event_emitter.add_listener('input', handle_data)
            return lambda: event_emitter.remove_listener('input', handle_data) if hasattr(event_emitter, 'remove_listener') else None
    
    return None

