"""
Component Decorator - Creates function components for the reconciler.

Similar to ReactPy's @component but works with our custom reconciler.
"""
from typing import Callable, Any
from functools import wraps
from inkpy.reconciler.element import create_element, Element


def component(func: Callable) -> Callable[..., Element]:
    """
    Decorator to create a function component.

    Usage:
        @component
        def Greeting(name: str = "World"):
            return create_element("ink-text", {}, f"Hello, {name}!")

        # Use like:
        element = Greeting(name="Test")
        # Or in JSX-like syntax:
        create_element(Greeting, {"name": "Test"})

    Args:
        func: Component function that returns an Element

    Returns:
        Wrapper that creates an Element with the function as type
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Element:
        # If called with positional args, treat first as children
        if args and not kwargs.get("children"):
            kwargs["children"] = list(args)
            args = ()

        # Create element with component function as type
        return create_element(func, kwargs)

    # Store reference to original function
    wrapper.__wrapped__ = func

    return wrapper

