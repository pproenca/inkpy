"""
useStderr hook module - provides access to stderr stream
"""
from reactpy.core.hooks import use_context
from inkpy.components.stderr_context import StderrContext

def use_stderr():
    """
    Hook that provides access to stderr stream and write function.
    
    Returns:
        Object with 'stderr' (TextIO) and 'write' (Callable) attributes
        
    Example:
        @component
        def App():
            stderr = use_stderr()
            stderr.write("Error message")
            return Text("Error written")
    """
    context_value = use_context(StderrContext)
    return context_value

