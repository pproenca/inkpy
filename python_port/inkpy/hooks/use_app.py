"""
useApp hook module - provides access to app-level functionality
"""
from reactpy.core.hooks import use_context
from inkpy.components.app_context import AppContext

def use_app():
    """
    Hook that exposes a method to manually exit the app (unmount).
    
    Returns:
        Object with 'exit' method that can be called to exit the app
        
    Example:
        @component
        def App():
            app = use_app()
            
            def handle_quit():
                app.exit()
            
            return Text("Press 'q' to quit")
    """
    context_value = use_context(AppContext)
    return context_value

