"""
useFocus hook module - provides focus management for components
"""
import random
from typing import Optional, Dict, Any
from reactpy import use_effect, use_memo
from reactpy.core.hooks import use_context
from inkpy.components.focus_context import FocusContext
from inkpy.hooks.use_stdin import use_stdin

def use_focus(
    is_active: bool = True,
    auto_focus: bool = False,
    id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Hook that makes a component focusable.
    
    When the user presses Tab, Ink will switch focus to this component.
    If there are multiple components using useFocus, focus will be given
    in the order they are rendered.
    
    Args:
        is_active: Enable or disable this component's focus
        auto_focus: Auto-focus this component if there's no active component
        id: Custom ID for programmatic focusing
        
    Returns:
        Dict with 'is_focused' (bool) and 'focus' (Callable) attributes
        
    Example:
        @component
        def FocusableItem():
            focus = use_focus(auto_focus=True)
            return Text("Focused" if focus.is_focused else "Not focused")
    """
    stdin = use_stdin()
    focus_context = use_context(FocusContext)
    
    # Generate ID if not provided
    focus_id = use_memo(lambda: id or str(random.randint(10000, 99999)), [id])
    
    # Register/unregister with focus context
    # ReactPy's use_effect expects cleanup to be returned from the effect function
    def register_effect():
        focus_context['add'](focus_id, {'auto_focus': auto_focus})
        return lambda: focus_context['remove'](focus_id)
    
    use_effect(register_effect, dependencies=[focus_id, auto_focus])
    
    # Activate/deactivate based on is_active
    use_effect(
        lambda: focus_context['activate'](focus_id) if is_active else focus_context['deactivate'](focus_id),
        dependencies=[is_active, focus_id]
    )
    
    # Manage raw mode when active
    def raw_mode_effect():
        if hasattr(stdin, 'set_raw_mode') and is_active:
            stdin.set_raw_mode(True)
            return lambda: stdin.set_raw_mode(False) if hasattr(stdin, 'set_raw_mode') else None
        return None
    
    use_effect(raw_mode_effect, dependencies=[is_active])
    
    return {
        'is_focused': bool(focus_id) and focus_context.get('active_id') == focus_id,
        'focus': focus_context['focus']
    }

