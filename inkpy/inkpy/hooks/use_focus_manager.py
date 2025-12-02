"""
useFocusManager hook module - provides focus management control
"""

from typing import Any, Callable

from reactpy.core.hooks import use_context

from inkpy.components.focus_context import FocusContext


def use_focus_manager() -> dict[str, Callable[..., Any]]:
    """
    Hook that exposes methods to enable/disable focus management
    or manually switch focus between components.

    Returns:
        Dict with focus management methods:
        - enable_focus: Enable focus management
        - disable_focus: Disable focus management
        - focus_next: Switch to next focusable component
        - focus_previous: Switch to previous focusable component
        - focus: Switch focus to element with given ID

    Example:
        @component
        def App():
            manager = use_focus_manager()

            def handle_key(key):
                if key == 'n':
                    manager['focus_next']()

            return Box(Text("Press 'n' for next"))
    """
    focus_context = use_context(FocusContext)

    return {
        "enable_focus": focus_context["enable_focus"],
        "disable_focus": focus_context["disable_focus"],
        "focus_next": focus_context["focus_next"],
        "focus_previous": focus_context["focus_previous"],
        "focus": focus_context["focus"],
    }
