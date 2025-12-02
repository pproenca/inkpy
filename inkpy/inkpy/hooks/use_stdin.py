"""
useStdin hook module.

Ports use-stdin functionality from Ink.
Provides access to stdin stream and raw mode management.
"""

from reactpy.core.hooks import use_context

from inkpy.components.stdin_context import StdinContext


def use_stdin():
    """
    Hook for accessing stdin stream.

    Returns an object with:
    - stdin: The stdin stream
    - set_raw_mode: Function to enable/disable raw mode
    - is_raw_mode_supported: Whether raw mode is supported
    - internal_exitOnCtrlC: Whether to exit on Ctrl+C
    - internal_eventEmitter: Event emitter for input events

    Example:
        @component
        def App():
            stdin = use_stdin()
            # Access stdin['stdin'], stdin['set_raw_mode'], etc.
            return Text("Input handling")
    """
    # Get StdinContext value
    context_value = use_context(StdinContext)

    # Return context value directly (it's already a dict with all needed fields)
    return context_value
