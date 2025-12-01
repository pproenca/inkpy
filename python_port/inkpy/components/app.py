"""
App component - Root wrapper component for InkPy applications
"""
from typing import Optional, TextIO, Callable, Dict, Any, List
from reactpy import component, html, use_state, use_effect
from reactpy.core.hooks import use_context
from inkpy.components.app_context import AppContext
from inkpy.components.stdout_context import StdoutContext
from inkpy.components.stderr_context import StderrContext
from inkpy.components.focus_context import FocusContext

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
    # Focus state management
    is_focus_enabled, set_is_focus_enabled = use_state(True)
    active_focus_id, set_active_focus_id = use_state(None)
    focusables, set_focusables = use_state([])
    
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
    
    # Provide all contexts - ReactPy contexts are used as components
    return html.div(
        AppContext(
            value=app_context_value,
            children=[
                StdoutContext(
                    value=stdout_context_value,
                    children=[
                        StderrContext(
                            value=stderr_context_value,
                            children=[
                                FocusContext(
                                    value=focus_context_value,
                                    children=[children]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    )

