"""
useStdout hook module - provides access to stdout stream
"""
from reactpy.core.hooks import use_context
from inkpy.components.stdout_context import StdoutContext

def use_stdout():
    """
    Hook that provides access to stdout stream and write function.
    
    Returns:
        Object with 'stdout' (TextIO) and 'write' (Callable) attributes
        
    Example:
        @component
        def App():
            stdout = use_stdout()
            stdout.write("Hello, World!")
            return Text("Output written")
    """
    context_value = use_context(StdoutContext)
    return context_value

