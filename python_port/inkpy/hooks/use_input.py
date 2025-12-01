"""
useInput hook module.

Ports use-input functionality from Ink.
Provides a hook for handling user input in ReactPy components.
"""
from typing import Callable, Optional
from ..input.keypress import Key, parse_keypress, NON_ALPHANUMERIC_KEYS


def use_input(
    input_handler: Callable[[str, Key], None],
    is_active: bool = True
) -> None:
    """
    Hook for handling user input.
    
    This hook is used for handling user input. It's a more convenient
    alternative to using StdinContext and listening for data events.
    
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
    # In ReactPy, this would be implemented using use_effect and use_stdin
    # For now, this is a placeholder that will be integrated with ReactPy hooks
    # The actual implementation will:
    # 1. Use use_stdin() to get stdin access
    # 2. Use use_effect() to set up event listeners
    # 3. Parse input with parse_keypress
    # 4. Call input_handler with parsed input
    
    if not is_active:
        return
    
    # This will be implemented when we have ReactPy integration
    # For now, we just define the interface
    pass

