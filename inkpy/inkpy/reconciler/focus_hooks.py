"""
Focus Hooks for Custom Reconciler.

Provides focus management hooks:
- use_focus: Makes a component focusable
- use_focus_manager: Provides focus navigation controls
"""

import random
from dataclasses import dataclass
from typing import Any, Callable, Optional

from inkpy.reconciler.hooks import use_effect, use_ref

# Global focus state (similar to app_hooks pattern)
_focus_state: dict[str, Any] = {
    "active_id": None,
    "focusables": [],  # List of {id, is_active, auto_focus}
    "enabled": True,
}


def reset_focus_state():
    """Reset focus state (for testing)"""
    global _focus_state
    _focus_state = {
        "active_id": None,
        "focusables": [],
        "enabled": True,
    }


def get_focus_state() -> dict[str, Any]:
    """Get current focus state (for testing/debugging)"""
    return _focus_state


def _add_focusable(id: str, opts: dict[str, Any]):
    """Add a focusable component to the registry"""
    # Check if already exists
    existing = next((f for f in _focus_state["focusables"] if f["id"] == id), None)
    if existing:
        # Update existing entry
        existing["auto_focus"] = opts.get("auto_focus", False)
        existing["is_active"] = True
        return

    focusable = {
        "id": id,
        "is_active": True,
        "auto_focus": opts.get("auto_focus", False),
    }
    _focus_state["focusables"].append(focusable)

    # Auto-focus if requested and no active focus
    if opts.get("auto_focus") and _focus_state["active_id"] is None:
        _focus_state["active_id"] = id


def _remove_focusable(id: str):
    """Remove a focusable component from the registry"""
    _focus_state["focusables"] = [f for f in _focus_state["focusables"] if f["id"] != id]

    # Clear active if removed
    if _focus_state["active_id"] == id:
        _focus_state["active_id"] = None

        # Auto-focus first available if any
        active_focusables = [f for f in _focus_state["focusables"] if f["is_active"]]
        if active_focusables:
            _focus_state["active_id"] = active_focusables[0]["id"]


def _activate_focusable(id: str):
    """Activate a focusable component"""
    for f in _focus_state["focusables"]:
        if f["id"] == id:
            f["is_active"] = True
            break


def _deactivate_focusable(id: str):
    """Deactivate a focusable component"""
    for f in _focus_state["focusables"]:
        if f["id"] == id:
            f["is_active"] = False
            break

    # Clear active if deactivated
    if _focus_state["active_id"] == id:
        _focus_state["active_id"] = None


def _focus(id: str):
    """Focus a specific component by ID"""
    # Check if focusable and active
    focusable = next((f for f in _focus_state["focusables"] if f["id"] == id), None)
    if focusable and focusable["is_active"]:
        _focus_state["active_id"] = id


def _focus_next():
    """Focus the next focusable component"""
    active_focusables = [f for f in _focus_state["focusables"] if f["is_active"]]
    if not active_focusables:
        return

    current_id = _focus_state["active_id"]

    if current_id is None:
        # Focus first
        _focus_state["active_id"] = active_focusables[0]["id"]
        return

    # Find current index and move to next
    current_idx = next((i for i, f in enumerate(active_focusables) if f["id"] == current_id), -1)

    if current_idx == -1:
        # Current not found, focus first
        _focus_state["active_id"] = active_focusables[0]["id"]
    else:
        # Move to next (wrap around)
        next_idx = (current_idx + 1) % len(active_focusables)
        _focus_state["active_id"] = active_focusables[next_idx]["id"]


def _focus_previous():
    """Focus the previous focusable component"""
    active_focusables = [f for f in _focus_state["focusables"] if f["is_active"]]
    if not active_focusables:
        return

    current_id = _focus_state["active_id"]

    if current_id is None:
        # Focus last
        _focus_state["active_id"] = active_focusables[-1]["id"]
        return

    # Find current index and move to previous
    current_idx = next((i for i, f in enumerate(active_focusables) if f["id"] == current_id), -1)

    if current_idx == -1:
        # Current not found, focus last
        _focus_state["active_id"] = active_focusables[-1]["id"]
    else:
        # Move to previous (wrap around)
        prev_idx = (current_idx - 1) % len(active_focusables)
        _focus_state["active_id"] = active_focusables[prev_idx]["id"]


@dataclass
class UseFocusResult:
    """Result object from use_focus hook"""

    is_focused: bool
    focus: Callable[[], None]


def use_focus(
    is_active: bool = True,
    auto_focus: bool = False,
    id: Optional[str] = None,
) -> UseFocusResult:
    """
    Hook that makes a component focusable.

    When the user presses Tab, focus will switch between components.
    If there are multiple components using use_focus, focus will be given
    in the order they are rendered.

    Args:
        is_active: Enable or disable this component's focus
        auto_focus: Auto-focus this component if there's no active component
        id: Custom ID for programmatic focusing

    Returns:
        UseFocusResult with is_focused (bool) and focus (callable)

    Example:
        @component
        def FocusableItem():
            focus = use_focus(auto_focus=True)
            return Text("Focused" if focus.is_focused else "Not focused")
    """
    # Generate stable ID using ref
    id_ref = use_ref(id or f"focus-{random.randint(10000, 99999)}")
    focus_id = id_ref.current

    # Override with provided ID if given
    if id:
        focus_id = id
        id_ref.current = id

    # Register immediately during render (not in effect) for proper auto-focus
    # This ensures the focusable is registered before we check is_focused
    _add_focusable(focus_id, {"auto_focus": auto_focus})

    # Effect only handles cleanup
    def setup_focus():
        # Re-add in case it was removed
        _add_focusable(focus_id, {"auto_focus": auto_focus})

        def cleanup():
            _remove_focusable(focus_id)

        return cleanup

    use_effect(setup_focus, [focus_id, auto_focus])

    # Handle is_active changes
    if is_active:
        _activate_focusable(focus_id)
    else:
        _deactivate_focusable(focus_id)

    # Create focus callback for this component
    def focus_self():
        _focus(focus_id)

    return UseFocusResult(
        is_focused=_focus_state["active_id"] == focus_id,
        focus=focus_self,
    )


@dataclass
class UseFocusManagerResult:
    """Result object from use_focus_manager hook"""

    focus_next: Callable[[], None]
    focus_previous: Callable[[], None]
    focus: Callable[[str], None]
    enable_focus: Callable[[], None]
    disable_focus: Callable[[], None]


def use_focus_manager() -> UseFocusManagerResult:
    """
    Hook that provides focus navigation controls.

    Use this in a parent component to control focus navigation
    between child focusable components.

    Returns:
        UseFocusManagerResult with navigation methods:
        - focus_next(): Move focus to next component
        - focus_previous(): Move focus to previous component
        - focus(id): Focus a specific component by ID
        - enable_focus(): Enable focus system
        - disable_focus(): Disable focus system

    Example:
        @component
        def App():
            manager = use_focus_manager()

            def handle_input(input_str, key):
                if key.tab:
                    manager.focus_next()

            use_input(handle_input)
            return Box(...)
    """

    def enable():
        _focus_state["enabled"] = True

    def disable():
        _focus_state["enabled"] = False

    return UseFocusManagerResult(
        focus_next=_focus_next,
        focus_previous=_focus_previous,
        focus=_focus,
        enable_focus=enable,
        disable_focus=disable,
    )
