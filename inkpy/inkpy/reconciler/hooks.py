"""
Hooks System - React-like hooks for function components.

Provides:
- use_state: Local component state
- use_effect: Side effects after render
- use_context: Read context values
- use_memo: Memoized computations
- use_callback: Memoized callbacks
"""
from typing import Any, Callable, Optional, List, TypeVar, Generic
from dataclasses import dataclass, field
import threading

T = TypeVar('T')

# Thread-local storage for current fiber and context
_current_fiber = threading.local()
_current_hooks_context = threading.local()
_state_change_callback: Optional[Callable[[], None]] = None


@dataclass
class Hook:
    """Base hook storage"""
    pass


@dataclass
class StateHook(Hook):
    """State hook storage"""
    state: Any
    queue: List[Any] = field(default_factory=list)


@dataclass
class EffectHook(Hook):
    """Effect hook storage"""
    callback: Callable
    deps: Optional[List[Any]]
    cleanup: Optional[Callable] = None


@dataclass
class MemoHook(Hook):
    """Memo hook storage"""
    value: Any
    deps: Optional[List[Any]]


@dataclass
class Context(Generic[T]):
    """Context object for sharing values down the tree"""
    default_value: T
    _id: int = field(default_factory=lambda: id(object()))


class ContextProvider:
    """Marker class for context provider elements"""
    pass


def create_context(default_value: T) -> Context[T]:
    """Create a new context with a default value"""
    return Context(default_value=default_value)


class HooksContext:
    """
    Context manager for executing hooks within a fiber.

    Usage:
        with HooksContext(fiber) as ctx:
            value, set_value = use_state(0)
            use_effect(lambda: print("rendered"))
    """
    def __init__(self, fiber, on_state_change: Optional[Callable[[], None]] = None):
        self.fiber = fiber
        self.on_state_change = on_state_change
        self.pending_effects: List[EffectHook] = []
        self._prev_fiber = None
        self._prev_callback = None
        self._prev_context = None

    def __enter__(self):
        global _state_change_callback
        self._prev_fiber = getattr(_current_fiber, 'value', None)
        self._prev_callback = _state_change_callback
        self._prev_context = getattr(_current_hooks_context, 'value', None)
        _current_fiber.value = self.fiber
        _current_hooks_context.value = self
        _state_change_callback = self.on_state_change
        self.fiber.hook_index = 0
        return self

    def __exit__(self, *args):
        global _state_change_callback
        _current_fiber.value = self._prev_fiber
        _current_hooks_context.value = self._prev_context
        _state_change_callback = self._prev_callback


def _get_current_fiber():
    """Get the currently rendering fiber"""
    fiber = getattr(_current_fiber, 'value', None)
    if fiber is None:
        raise RuntimeError("Hooks can only be called inside a component")
    return fiber


def _get_hook(hook_type: type) -> Any:
    """Get or create a hook at the current index"""
    fiber = _get_current_fiber()

    # Check if we have an existing hook
    if fiber.hook_index < len(fiber.hooks):
        hook = fiber.hooks[fiber.hook_index]
        fiber.hook_index += 1
        return hook

    # Create new hook
    hook = hook_type.__new__(hook_type)
    fiber.hooks.append(hook)
    fiber.hook_index += 1
    return hook


def use_state(initial_value: T) -> tuple[T, Callable[[T], None]]:
    """
    Returns a stateful value and a function to update it.

    Args:
        initial_value: Initial state value or lazy initializer function

    Returns:
        Tuple of (current_value, setter_function)
    """
    fiber = _get_current_fiber()
    hook_index = fiber.hook_index

    # Get or create hook
    if hook_index < len(fiber.hooks):
        hook = fiber.hooks[hook_index]
    else:
        # Initialize state
        if callable(initial_value):
            state = initial_value()
        else:
            state = initial_value
        hook = StateHook(state=state)
        fiber.hooks.append(hook)

    fiber.hook_index += 1

    # Process any queued updates
    for update in hook.queue:
        if callable(update):
            hook.state = update(hook.state)
        else:
            hook.state = update
    hook.queue.clear()

    # Create setter that schedules update
    def set_state(new_value):
        hook.queue.append(new_value)
        if _state_change_callback:
            _state_change_callback()

    return hook.state, set_state


def use_effect(callback: Callable, deps: Optional[List[Any]] = None) -> None:
    """
    Accepts a function that contains imperative, possibly effectful code.

    Args:
        callback: Effect function, may return cleanup function
        deps: Dependency array (None = run every render, [] = run once)
    """
    fiber = _get_current_fiber()
    hook_index = fiber.hook_index

    # Get or create hook
    if hook_index < len(fiber.hooks):
        hook = fiber.hooks[hook_index]
        old_deps = hook.deps

        # Check if deps changed
        should_run = deps is None or old_deps is None or _deps_changed(old_deps, deps)

        if should_run:
            hook.callback = callback
            hook.deps = deps
    else:
        hook = EffectHook(callback=callback, deps=deps)
        fiber.hooks.append(hook)

    fiber.hook_index += 1

    # Add to current HooksContext's pending_effects for later execution
    ctx = getattr(_current_hooks_context, 'value', None)
    if ctx is not None:
        ctx.pending_effects.append(hook)


def use_context(context: Context[T]) -> T:
    """
    Accepts a context object and returns the current context value.

    Args:
        context: Context object created by create_context

    Returns:
        Current context value from nearest provider
    """
    fiber = _get_current_fiber()

    # Walk up the tree to find provider
    current = fiber.parent
    while current:
        if (current.element_type == ContextProvider and
            current.props.get("context") == context):
            return current.props.get("value", context.default_value)
        current = current.parent

    return context.default_value


def use_memo(factory: Callable[[], T], deps: Optional[List[Any]] = None) -> T:
    """
    Returns a memoized value that only recomputes when deps change.

    Args:
        factory: Function that computes the value
        deps: Dependency array

    Returns:
        Memoized value
    """
    fiber = _get_current_fiber()
    hook_index = fiber.hook_index

    # Get or create hook
    if hook_index < len(fiber.hooks):
        hook = fiber.hooks[hook_index]

        # Check if deps changed
        if deps is not None and hook.deps is not None:
            if not _deps_changed(hook.deps, deps):
                fiber.hook_index += 1
                return hook.value

        # Recompute
        hook.value = factory()
        hook.deps = deps
    else:
        hook = MemoHook(value=factory(), deps=deps)
        fiber.hooks.append(hook)

    fiber.hook_index += 1
    return hook.value


def use_callback(callback: Callable, deps: Optional[List[Any]] = None) -> Callable:
    """
    Returns a memoized callback that only changes when deps change.

    Args:
        callback: Callback function
        deps: Dependency array

    Returns:
        Memoized callback
    """
    return use_memo(lambda: callback, deps)


def _deps_changed(old_deps: List[Any], new_deps: List[Any]) -> bool:
    """Check if dependencies have changed"""
    if len(old_deps) != len(new_deps):
        return True

    for old, new in zip(old_deps, new_deps):
        if old is not new and old != new:
            return True

    return False

