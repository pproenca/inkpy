# Custom Reconciler Implementation Plan

> **Goal:** Build a custom React-like reconciler for InkPy that provides full parity with Ink's `react-reconciler` architecture
>
> **Tech Stack:** Python 3.9+, asyncio, Poga (Yoga layout)
>
> **Skills Reference:** See `@.cursor/skills/test-driven-development.md` for TDD protocol
>
> **Last Updated:** 2025-12-02

---

## Executive Summary

This plan creates a custom component system and reconciler for InkPy that mirrors Ink's architecture. The key insight is that ReactPy's `Layout` class doesn't provide the synchronous, batched updates that Ink relies on. We need to build our own.

### Architecture Comparison

| Feature | Ink (React) | Current InkPy (ReactPy) | New InkPy (Custom) |
|---------|-------------|-------------------------|-------------------|
| Component System | React components | ReactPy `@component` | Custom `Component` class |
| State Management | `useState` → reconciler queue | `use_state` → Layout queue | Custom `use_state` → immediate render |
| Batched Updates | `batchedUpdates()` | Not available | Custom `batch_updates()` |
| Render Trigger | `resetAfterCommit()` | Manual `await layout.render()` | Automatic on state change |
| Synchronous Updates | `updateContainerSync()` | Async only | Sync `update_container()` |

---

## Phase 1: Core Reconciler Infrastructure

### Task 1.1: Create Fiber Node Types

**Files:**
- Create: `inkpy/inkpy/reconciler/fiber.py`
- Test: `inkpy/tests/reconciler/test_fiber.py`

**Step 1: Write the failing test**
```python
# tests/reconciler/test_fiber.py
import pytest
from inkpy.reconciler.fiber import FiberNode, FiberTag, create_fiber

def test_create_host_fiber():
    """Test creating a fiber for a host element (ink-box)"""
    fiber = create_fiber(
        tag=FiberTag.HOST_COMPONENT,
        element_type="ink-box",
        props={"style": {"padding": 1}},
    )
    
    assert fiber.tag == FiberTag.HOST_COMPONENT
    assert fiber.element_type == "ink-box"
    assert fiber.props == {"style": {"padding": 1}}
    assert fiber.dom is None
    assert fiber.child is None
    assert fiber.sibling is None
    assert fiber.parent is None

def test_create_function_fiber():
    """Test creating a fiber for a function component"""
    def MyComponent(props):
        return {"type": "ink-box", "props": {}}
    
    fiber = create_fiber(
        tag=FiberTag.FUNCTION_COMPONENT,
        element_type=MyComponent,
        props={"text": "hello"},
    )
    
    assert fiber.tag == FiberTag.FUNCTION_COMPONENT
    assert fiber.element_type == MyComponent
    assert fiber.props == {"text": "hello"}

def test_fiber_alternate():
    """Test fiber alternate for double buffering"""
    fiber1 = create_fiber(FiberTag.HOST_COMPONENT, "ink-box", {})
    fiber2 = create_fiber(FiberTag.HOST_COMPONENT, "ink-box", {"updated": True})
    
    fiber1.alternate = fiber2
    fiber2.alternate = fiber1
    
    assert fiber1.alternate is fiber2
    assert fiber2.alternate is fiber1
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest inkpy/tests/reconciler/test_fiber.py -v
```
Expected: FAIL with "ModuleNotFoundError: No module named 'inkpy.reconciler'"

**Step 3: Write minimal implementation**
```python
# inkpy/inkpy/reconciler/fiber.py
"""
Fiber Node - The building block of the reconciler's work-in-progress tree.

Based on React Fiber architecture:
- Each fiber represents a unit of work
- Fibers form a linked list tree structure
- Double buffering via alternate pointers
"""
from enum import IntEnum, auto
from typing import Any, Dict, Optional, Callable, Union, List
from dataclasses import dataclass, field

class FiberTag(IntEnum):
    """Fiber node type tags"""
    HOST_ROOT = auto()          # Root of the fiber tree
    HOST_COMPONENT = auto()     # DOM element (ink-box, ink-text)
    FUNCTION_COMPONENT = auto() # Function component
    CLASS_COMPONENT = auto()    # Class component (for future use)
    TEXT_NODE = auto()          # Text content

class EffectTag(IntEnum):
    """Side effect tags for commit phase"""
    NONE = 0
    PLACEMENT = 1       # New node to insert
    UPDATE = 2          # Node needs update
    DELETION = 4        # Node to remove
    PLACEMENT_AND_UPDATE = 3  # PLACEMENT | UPDATE

@dataclass
class FiberNode:
    """
    A fiber node representing a component or element in the tree.
    
    Uses linked list structure:
    - child: first child fiber
    - sibling: next sibling fiber
    - parent: parent fiber (called 'return' in React)
    """
    # Type information
    tag: FiberTag
    element_type: Union[str, Callable, None]  # "ink-box" or component function
    key: Optional[str] = None
    
    # Props and state
    props: Dict[str, Any] = field(default_factory=dict)
    memoized_state: Any = None  # For hooks
    
    # Tree structure (linked list)
    child: Optional['FiberNode'] = None
    sibling: Optional['FiberNode'] = None
    parent: Optional['FiberNode'] = None  # 'return' in React
    index: int = 0
    
    # DOM reference
    dom: Any = None  # DOMElement or TextNode
    
    # Double buffering
    alternate: Optional['FiberNode'] = None
    
    # Effects
    effect_tag: EffectTag = EffectTag.NONE
    effects: List['FiberNode'] = field(default_factory=list)
    
    # Hooks
    hooks: List[Any] = field(default_factory=list)
    hook_index: int = 0

def create_fiber(
    tag: FiberTag,
    element_type: Union[str, Callable, None],
    props: Dict[str, Any],
    key: Optional[str] = None,
) -> FiberNode:
    """Factory function to create a fiber node"""
    return FiberNode(
        tag=tag,
        element_type=element_type,
        props=props,
        key=key,
    )

def create_root_fiber() -> FiberNode:
    """Create the root fiber for the tree"""
    return FiberNode(
        tag=FiberTag.HOST_ROOT,
        element_type=None,
        props={},
    )
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest inkpy/tests/reconciler/test_fiber.py -v
```
Expected: PASS

**Step 5: Create __init__.py**
```python
# inkpy/inkpy/reconciler/__init__.py
"""Custom Reconciler Package"""
from .fiber import FiberNode, FiberTag, EffectTag, create_fiber, create_root_fiber

__all__ = [
    'FiberNode',
    'FiberTag', 
    'EffectTag',
    'create_fiber',
    'create_root_fiber',
]
```

---

### Task 1.2: Create Element Factory

**Files:**
- Create: `inkpy/inkpy/reconciler/element.py`
- Test: `inkpy/tests/reconciler/test_element.py`

**Step 1: Write the failing test**
```python
# tests/reconciler/test_element.py
import pytest
from inkpy.reconciler.element import create_element, Element

def test_create_element_with_type():
    """Test creating an element with type and props"""
    element = create_element("ink-box", {"padding": 1})
    
    assert element.type == "ink-box"
    assert element.props == {"padding": 1, "children": []}
    assert element.key is None

def test_create_element_with_children():
    """Test creating an element with children"""
    child1 = create_element("ink-text", {}, "Hello")
    child2 = create_element("ink-text", {}, "World")
    parent = create_element("ink-box", {}, child1, child2)
    
    assert len(parent.props["children"]) == 2
    assert parent.props["children"][0] is child1
    assert parent.props["children"][1] is child2

def test_create_element_with_string_child():
    """Test creating an element with string children"""
    element = create_element("ink-text", {}, "Hello World")
    
    assert element.props["children"] == ["Hello World"]

def test_create_element_with_function_type():
    """Test creating an element with a function component"""
    def MyComponent(props):
        return create_element("ink-box", props)
    
    element = create_element(MyComponent, {"name": "test"})
    
    assert element.type == MyComponent
    assert element.props["name"] == "test"

def test_create_element_with_key():
    """Test creating an element with a key"""
    element = create_element("ink-box", {"key": "unique-id"})
    
    assert element.key == "unique-id"
    assert "key" not in element.props  # key should be extracted
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest inkpy/tests/reconciler/test_element.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**
```python
# inkpy/inkpy/reconciler/element.py
"""
Element - Immutable description of what to render.

Similar to React.createElement() - creates element descriptors
that the reconciler uses to build the fiber tree.
"""
from typing import Any, Dict, Optional, Callable, Union, List
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Element:
    """
    An immutable element descriptor.
    
    Elements describe what should be rendered but don't contain
    any state or lifecycle - that's handled by fibers.
    """
    type: Union[str, Callable]  # "ink-box" or component function
    props: Dict[str, Any]
    key: Optional[str] = None

def create_element(
    element_type: Union[str, Callable],
    props: Optional[Dict[str, Any]] = None,
    *children: Any,
) -> Element:
    """
    Create an element descriptor.
    
    Args:
        element_type: Element type ("ink-box", "ink-text") or component function
        props: Properties for the element
        *children: Child elements or text content
    
    Returns:
        Element descriptor
    
    Example:
        create_element("ink-box", {"padding": 1},
            create_element("ink-text", {}, "Hello")
        )
    """
    props = dict(props) if props else {}
    
    # Extract key from props
    key = props.pop("key", None)
    
    # Normalize children
    if children:
        if len(children) == 1:
            # Single child - could be element, string, or list
            child = children[0]
            if isinstance(child, (list, tuple)):
                props["children"] = list(child)
            else:
                props["children"] = [child]
        else:
            props["children"] = list(children)
    else:
        props["children"] = props.get("children", [])
    
    # Ensure children is always a list
    if not isinstance(props["children"], list):
        props["children"] = [props["children"]]
    
    return Element(
        type=element_type,
        props=props,
        key=key,
    )

# Convenience alias
h = create_element
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest inkpy/tests/reconciler/test_element.py -v
```
Expected: PASS

---

### Task 1.3: Create Hooks System

**Files:**
- Create: `inkpy/inkpy/reconciler/hooks.py`
- Test: `inkpy/tests/reconciler/test_hooks.py`

**Step 1: Write the failing test**
```python
# tests/reconciler/test_hooks.py
import pytest
from inkpy.reconciler.hooks import (
    use_state, use_effect, use_context, use_memo, use_callback,
    HooksContext, create_context, ContextProvider,
)
from inkpy.reconciler.fiber import FiberNode, FiberTag

def test_use_state_initial_value():
    """Test use_state returns initial value on first render"""
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    
    with HooksContext(fiber):
        value, set_value = use_state(42)
    
    assert value == 42
    assert callable(set_value)

def test_use_state_lazy_initial():
    """Test use_state with lazy initializer"""
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    called = []
    
    def expensive_init():
        called.append(True)
        return 100
    
    with HooksContext(fiber):
        value, _ = use_state(expensive_init)
    
    assert value == 100
    assert len(called) == 1

def test_use_state_setter_schedules_update():
    """Test that set_state schedules a re-render"""
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    scheduled = []
    
    with HooksContext(fiber, on_state_change=lambda: scheduled.append(True)):
        value, set_value = use_state(0)
        set_value(1)
    
    assert len(scheduled) == 1

def test_use_effect_runs_after_render():
    """Test use_effect callback is collected for later execution"""
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    effects = []
    
    def effect():
        effects.append("ran")
        return lambda: effects.append("cleanup")
    
    with HooksContext(fiber) as ctx:
        use_effect(effect)
    
    # Effect should be queued, not run yet
    assert len(effects) == 0
    assert len(ctx.pending_effects) == 1

def test_use_context_reads_value():
    """Test use_context reads from context provider"""
    ThemeContext = create_context("light")
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    
    # Simulate context provider in tree
    provider_fiber = FiberNode(
        tag=FiberTag.HOST_COMPONENT,
        element_type=ContextProvider,
        props={"context": ThemeContext, "value": "dark"},
    )
    fiber.parent = provider_fiber
    
    with HooksContext(fiber):
        theme = use_context(ThemeContext)
    
    assert theme == "dark"

def test_use_memo_caches_value():
    """Test use_memo only recomputes when deps change"""
    fiber = FiberNode(tag=FiberTag.FUNCTION_COMPONENT, element_type=lambda: None)
    compute_count = [0]
    
    def compute():
        compute_count[0] += 1
        return compute_count[0]
    
    # First render
    with HooksContext(fiber):
        result1 = use_memo(compute, [1, 2])
    
    # Second render with same deps (simulated by reusing hooks)
    fiber.hook_index = 0
    with HooksContext(fiber):
        result2 = use_memo(compute, [1, 2])
    
    assert result1 == 1
    assert result2 == 1  # Should be cached
    assert compute_count[0] == 1
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest inkpy/tests/reconciler/test_hooks.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**
```python
# inkpy/inkpy/reconciler/hooks.py
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
from contextlib import contextmanager
import threading

T = TypeVar('T')

# Thread-local storage for current fiber
_current_fiber = threading.local()
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
    
    def __enter__(self):
        global _state_change_callback
        self._prev_fiber = getattr(_current_fiber, 'value', None)
        self._prev_callback = _state_change_callback
        _current_fiber.value = self.fiber
        _state_change_callback = self.on_state_change
        self.fiber.hook_index = 0
        return self
    
    def __exit__(self, *args):
        global _state_change_callback
        _current_fiber.value = self._prev_fiber
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
    
    # Queue effect for later execution
    ctx = getattr(_current_fiber, 'context', None)
    if hasattr(_current_fiber, 'value') and hasattr(_current_fiber.value, 'pending_effects'):
        pass  # Will be collected by HooksContext

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
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest inkpy/tests/reconciler/test_hooks.py -v
```
Expected: PASS

---

### Task 1.4: Create Reconciler Core

**Files:**
- Create: `inkpy/inkpy/reconciler/reconciler.py`
- Test: `inkpy/tests/reconciler/test_reconciler.py`

**Step 1: Write the failing test**
```python
# tests/reconciler/test_reconciler.py
import pytest
from inkpy.reconciler.reconciler import Reconciler
from inkpy.reconciler.element import create_element
from inkpy.reconciler.fiber import FiberTag

def test_reconciler_initial_render():
    """Test reconciler performs initial render"""
    rendered = []
    
    def on_commit(root_dom):
        rendered.append(root_dom)
    
    reconciler = Reconciler(on_commit=on_commit)
    
    element = create_element("ink-box", {"padding": 1},
        create_element("ink-text", {}, "Hello")
    )
    
    reconciler.render(element)
    
    assert len(rendered) == 1
    assert rendered[0].node_name == "ink-root"
    assert len(rendered[0].child_nodes) == 1

def test_reconciler_update():
    """Test reconciler handles updates"""
    commits = []
    
    reconciler = Reconciler(on_commit=lambda root: commits.append(root))
    
    # Initial render
    reconciler.render(create_element("ink-box", {}, "First"))
    
    # Update
    reconciler.render(create_element("ink-box", {}, "Second"))
    
    assert len(commits) == 2

def test_reconciler_function_component():
    """Test reconciler handles function components"""
    commits = []
    
    def Greeting(props):
        return create_element("ink-text", {}, f"Hello, {props['name']}!")
    
    reconciler = Reconciler(on_commit=lambda root: commits.append(root))
    reconciler.render(create_element(Greeting, {"name": "World"}))
    
    assert len(commits) == 1

def test_reconciler_state_update_triggers_rerender():
    """Test that state changes trigger re-render"""
    from inkpy.reconciler.hooks import use_state, HooksContext
    
    renders = []
    set_count_ref = [None]
    
    def Counter(props):
        count, set_count = use_state(0)
        set_count_ref[0] = set_count
        renders.append(count)
        return create_element("ink-text", {}, str(count))
    
    reconciler = Reconciler()
    reconciler.render(create_element(Counter, {}))
    
    assert renders == [0]
    
    # Trigger state update
    set_count_ref[0](1)
    reconciler.flush_sync()
    
    assert renders == [0, 1]

def test_reconciler_batched_updates():
    """Test that multiple state updates are batched"""
    from inkpy.reconciler.hooks import use_state
    
    renders = []
    setters = {}
    
    def MultiState(props):
        a, set_a = use_state(0)
        b, set_b = use_state(0)
        setters['a'] = set_a
        setters['b'] = set_b
        renders.append((a, b))
        return create_element("ink-text", {}, f"{a},{b}")
    
    reconciler = Reconciler()
    reconciler.render(create_element(MultiState, {}))
    
    assert renders == [(0, 0)]
    
    # Batch multiple updates
    reconciler.batch_updates(lambda: (
        setters['a'](1),
        setters['b'](2),
    ))
    reconciler.flush_sync()
    
    # Should only render once with both updates
    assert renders == [(0, 0), (1, 2)]
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest inkpy/tests/reconciler/test_reconciler.py -v
```
Expected: FAIL

**Step 3: Write implementation** (This is the core - more complex)
```python
# inkpy/inkpy/reconciler/reconciler.py
"""
Reconciler - The core of the custom component system.

Implements a simplified React Fiber reconciler that:
1. Builds a fiber tree from elements
2. Reconciles changes (diffing)
3. Commits changes to DOM
4. Handles state updates synchronously
"""
from typing import Any, Callable, Optional, List, Dict, Union
from dataclasses import dataclass
from inkpy.reconciler.fiber import (
    FiberNode, FiberTag, EffectTag, create_fiber, create_root_fiber
)
from inkpy.reconciler.element import Element
from inkpy.reconciler.hooks import HooksContext
from inkpy.dom import (
    create_node, create_text_node, append_child_node, 
    remove_child_node, set_style, set_attribute, DOMElement
)
from inkpy.layout.styles import apply_styles

class Reconciler:
    """
    Custom reconciler for InkPy.
    
    Provides synchronous rendering with batched updates,
    mirroring React's reconciler behavior.
    """
    
    def __init__(
        self,
        on_commit: Optional[Callable[[DOMElement], None]] = None,
        on_compute_layout: Optional[Callable[[], None]] = None,
    ):
        self.on_commit = on_commit
        self.on_compute_layout = on_compute_layout
        
        # Fiber tree roots
        self.current_root: Optional[FiberNode] = None
        self.wip_root: Optional[FiberNode] = None  # Work in progress
        
        # DOM root
        self.root_dom: Optional[DOMElement] = None
        
        # Update queue
        self._pending_updates: List[Callable] = []
        self._is_batching = False
        self._needs_render = False
        
        # Deletions to process
        self._deletions: List[FiberNode] = []
    
    def render(self, element: Element) -> None:
        """
        Render an element tree.
        
        This is the entry point - creates or updates the fiber tree
        and commits changes to DOM.
        """
        # Create root DOM if needed
        if self.root_dom is None:
            self.root_dom = create_node("ink-root")
        
        # Create work-in-progress root
        self.wip_root = create_fiber(
            tag=FiberTag.HOST_ROOT,
            element_type=None,
            props={"children": [element]},
        )
        self.wip_root.dom = self.root_dom
        self.wip_root.alternate = self.current_root
        
        self._deletions = []
        
        # Perform work
        self._perform_work(self.wip_root)
        
        # Commit
        self._commit_root()
    
    def flush_sync(self) -> None:
        """Flush any pending updates synchronously"""
        if self._needs_render and self.current_root:
            # Re-render with current element
            element = self.current_root.props.get("children", [None])[0]
            if element:
                self.render(element)
        self._needs_render = False
    
    def batch_updates(self, callback: Callable) -> None:
        """
        Batch multiple state updates into a single render.
        
        Args:
            callback: Function that performs state updates
        """
        self._is_batching = True
        try:
            callback()
        finally:
            self._is_batching = False
    
    def schedule_update(self) -> None:
        """Schedule a re-render (called by hooks)"""
        self._needs_render = True
        if not self._is_batching:
            self.flush_sync()
    
    def _perform_work(self, fiber: FiberNode) -> None:
        """
        Perform reconciliation work on a fiber.
        
        This is the "render phase" - builds the fiber tree.
        """
        # Process this fiber
        if fiber.tag == FiberTag.FUNCTION_COMPONENT:
            self._update_function_component(fiber)
        elif fiber.tag == FiberTag.HOST_ROOT:
            self._update_host_root(fiber)
        elif fiber.tag == FiberTag.HOST_COMPONENT:
            self._update_host_component(fiber)
        elif fiber.tag == FiberTag.TEXT_NODE:
            self._update_text_node(fiber)
        
        # Process children depth-first
        if fiber.child:
            self._perform_work(fiber.child)
        
        # Process siblings
        if fiber.sibling:
            self._perform_work(fiber.sibling)
    
    def _update_function_component(self, fiber: FiberNode) -> None:
        """Update a function component fiber"""
        # Set up hooks context
        with HooksContext(fiber, on_state_change=self.schedule_update):
            # Call the component function
            children = fiber.element_type(fiber.props)
        
        # Normalize children
        if not isinstance(children, list):
            children = [children] if children else []
        
        # Reconcile children
        self._reconcile_children(fiber, children)
    
    def _update_host_root(self, fiber: FiberNode) -> None:
        """Update the root fiber"""
        children = fiber.props.get("children", [])
        self._reconcile_children(fiber, children)
    
    def _update_host_component(self, fiber: FiberNode) -> None:
        """Update a host component (DOM element) fiber"""
        # Create DOM node if needed
        if fiber.dom is None:
            fiber.dom = self._create_dom(fiber)
        
        # Reconcile children
        children = fiber.props.get("children", [])
        self._reconcile_children(fiber, children)
    
    def _update_text_node(self, fiber: FiberNode) -> None:
        """Update a text node fiber"""
        if fiber.dom is None:
            fiber.dom = create_text_node(fiber.props.get("text", ""))
    
    def _create_dom(self, fiber: FiberNode) -> DOMElement:
        """Create a DOM node for a fiber"""
        node = create_node(fiber.element_type)
        
        # Apply props
        for key, value in fiber.props.items():
            if key == "children":
                continue
            if key == "style":
                set_style(node, value)
                if node.yoga_node and value:
                    apply_styles(node.yoga_node, value)
            else:
                set_attribute(node, key, value)
        
        return node
    
    def _reconcile_children(
        self, 
        parent_fiber: FiberNode, 
        elements: List[Union[Element, str, None]]
    ) -> None:
        """
        Reconcile children elements against existing fibers.
        
        This is the diffing algorithm - determines what changed.
        """
        # Get old fiber (first child of alternate)
        old_fiber = parent_fiber.alternate.child if parent_fiber.alternate else None
        
        prev_sibling: Optional[FiberNode] = None
        index = 0
        
        while index < len(elements) or old_fiber:
            element = elements[index] if index < len(elements) else None
            new_fiber: Optional[FiberNode] = None
            
            # Check if same type
            same_type = (
                old_fiber and 
                element and 
                self._get_element_type(element) == self._get_fiber_type(old_fiber)
            )
            
            if same_type:
                # Update existing fiber
                new_fiber = create_fiber(
                    tag=old_fiber.tag,
                    element_type=old_fiber.element_type,
                    props=self._get_element_props(element),
                    key=self._get_element_key(element),
                )
                new_fiber.dom = old_fiber.dom
                new_fiber.parent = parent_fiber
                new_fiber.alternate = old_fiber
                new_fiber.effect_tag = EffectTag.UPDATE
                new_fiber.hooks = old_fiber.hooks  # Preserve hooks
                
            elif element:
                # Create new fiber
                new_fiber = self._create_fiber_from_element(element)
                new_fiber.parent = parent_fiber
                new_fiber.effect_tag = EffectTag.PLACEMENT
            
            if old_fiber and not same_type:
                # Mark for deletion
                old_fiber.effect_tag = EffectTag.DELETION
                self._deletions.append(old_fiber)
            
            # Move to next old fiber
            if old_fiber:
                old_fiber = old_fiber.sibling
            
            # Link new fiber
            if new_fiber:
                if index == 0:
                    parent_fiber.child = new_fiber
                elif prev_sibling:
                    prev_sibling.sibling = new_fiber
                
                prev_sibling = new_fiber
            
            index += 1
    
    def _create_fiber_from_element(self, element: Union[Element, str]) -> FiberNode:
        """Create a fiber from an element"""
        if isinstance(element, str):
            return create_fiber(
                tag=FiberTag.TEXT_NODE,
                element_type="#text",
                props={"text": element},
            )
        
        if callable(element.type):
            return create_fiber(
                tag=FiberTag.FUNCTION_COMPONENT,
                element_type=element.type,
                props=element.props,
                key=element.key,
            )
        
        return create_fiber(
            tag=FiberTag.HOST_COMPONENT,
            element_type=element.type,
            props=element.props,
            key=element.key,
        )
    
    def _get_element_type(self, element: Union[Element, str, None]) -> Any:
        """Get the type of an element"""
        if element is None:
            return None
        if isinstance(element, str):
            return "#text"
        return element.type
    
    def _get_element_props(self, element: Union[Element, str]) -> Dict:
        """Get props from an element"""
        if isinstance(element, str):
            return {"text": element}
        return element.props
    
    def _get_element_key(self, element: Union[Element, str, None]) -> Optional[str]:
        """Get key from an element"""
        if isinstance(element, Element):
            return element.key
        return None
    
    def _get_fiber_type(self, fiber: FiberNode) -> Any:
        """Get the type of a fiber"""
        return fiber.element_type
    
    def _commit_root(self) -> None:
        """
        Commit phase - apply changes to DOM.
        
        This is where side effects happen.
        """
        # Process deletions
        for fiber in self._deletions:
            self._commit_deletion(fiber)
        
        # Commit work
        if self.wip_root.child:
            self._commit_work(self.wip_root.child)
        
        # Swap roots
        self.current_root = self.wip_root
        self.wip_root = None
        
        # Trigger callbacks
        if self.on_compute_layout:
            self.on_compute_layout()
        
        if self.on_commit and self.root_dom:
            self.on_commit(self.root_dom)
    
    def _commit_work(self, fiber: FiberNode) -> None:
        """Commit a fiber's changes to DOM"""
        if not fiber:
            return
        
        # Find parent DOM
        parent_fiber = fiber.parent
        while parent_fiber and not parent_fiber.dom:
            parent_fiber = parent_fiber.parent
        parent_dom = parent_fiber.dom if parent_fiber else None
        
        if fiber.effect_tag == EffectTag.PLACEMENT and fiber.dom:
            # Insert new node
            if parent_dom:
                append_child_node(parent_dom, fiber.dom)
                
        elif fiber.effect_tag == EffectTag.UPDATE and fiber.dom:
            # Update existing node
            self._update_dom(fiber.dom, fiber.alternate.props, fiber.props)
        
        # Recurse
        self._commit_work(fiber.child)
        self._commit_work(fiber.sibling)
    
    def _commit_deletion(self, fiber: FiberNode) -> None:
        """Remove a fiber's DOM node"""
        if fiber.dom:
            # Find parent DOM
            parent_fiber = fiber.parent
            while parent_fiber and not parent_fiber.dom:
                parent_fiber = parent_fiber.parent
            
            if parent_fiber and parent_fiber.dom:
                remove_child_node(parent_fiber.dom, fiber.dom)
        elif fiber.child:
            # Function component - recurse to find DOM
            self._commit_deletion(fiber.child)
    
    def _update_dom(
        self, 
        dom: DOMElement, 
        old_props: Dict, 
        new_props: Dict
    ) -> None:
        """Update DOM node properties"""
        # Remove old props
        for key in old_props:
            if key == "children":
                continue
            if key not in new_props:
                if key == "style":
                    set_style(dom, {})
                else:
                    set_attribute(dom, key, None)
        
        # Set new props
        for key, value in new_props.items():
            if key == "children":
                continue
            if old_props.get(key) != value:
                if key == "style":
                    set_style(dom, value)
                    if dom.yoga_node and value:
                        apply_styles(dom.yoga_node, value)
                else:
                    set_attribute(dom, key, value)
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest inkpy/tests/reconciler/test_reconciler.py -v
```
Expected: PASS

---

## Phase 2: Component Decorator and Integration

### Task 2.1: Create Component Decorator

**Files:**
- Create: `inkpy/inkpy/reconciler/component.py`
- Test: `inkpy/tests/reconciler/test_component.py`

**Step 1: Write the failing test**
```python
# tests/reconciler/test_component.py
import pytest
from inkpy.reconciler.component import component
from inkpy.reconciler.element import create_element
from inkpy.reconciler.hooks import use_state

def test_component_decorator():
    """Test @component decorator creates a function component"""
    @component
    def Greeting(name: str = "World"):
        return create_element("ink-text", {}, f"Hello, {name}!")
    
    # Should be callable and return an element
    element = Greeting(name="Test")
    
    assert element.type == Greeting.__wrapped__
    assert element.props["name"] == "Test"

def test_component_with_children():
    """Test component receives children prop"""
    @component
    def Container(children=None):
        return create_element("ink-box", {}, *children if children else [])
    
    child = create_element("ink-text", {}, "Child")
    element = Container(child)
    
    assert "children" in element.props

def test_component_with_state():
    """Test component can use hooks"""
    @component
    def Counter():
        count, set_count = use_state(0)
        return create_element("ink-text", {}, str(count))
    
    # Just verify it creates an element
    element = Counter()
    assert element.type == Counter.__wrapped__
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest inkpy/tests/reconciler/test_component.py -v
```
Expected: FAIL

**Step 3: Write minimal implementation**
```python
# inkpy/inkpy/reconciler/component.py
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
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest inkpy/tests/reconciler/test_component.py -v
```
Expected: PASS

---

### Task 2.2: Integrate with Existing InkPy

**Files:**
- Modify: `inkpy/inkpy/ink.py`
- Modify: `inkpy/inkpy/render.py`
- Test: `inkpy/tests/test_integration.py`

**Step 1: Write the failing test**
```python
# tests/test_integration.py
import pytest
import asyncio
from inkpy import render
from inkpy.reconciler.component import component
from inkpy.reconciler.element import create_element
from inkpy.reconciler.hooks import use_state
from inkpy.components import Box, Text

def test_render_with_custom_reconciler():
    """Test render() works with custom reconciler"""
    @component
    def App():
        return create_element("ink-box", {},
            create_element("ink-text", {}, "Hello World")
        )
    
    instance = render(App(), debug=True)
    
    # Should render without error
    assert instance is not None
    instance.unmount()

def test_interactive_state_updates():
    """Test that state updates trigger re-renders"""
    renders = []
    set_count_ref = [None]
    
    @component
    def Counter():
        count, set_count = use_state(0)
        set_count_ref[0] = set_count
        renders.append(count)
        return create_element("ink-text", {}, str(count))
    
    instance = render(Counter(), debug=True)
    
    assert renders == [0]
    
    # Trigger state update
    set_count_ref[0](1)
    
    # State update should trigger re-render synchronously
    assert renders == [0, 1]
    
    instance.unmount()
```

**Step 2: Run test to verify it fails**
```bash
uv run pytest inkpy/tests/test_integration.py -v
```
Expected: FAIL (current implementation doesn't use custom reconciler)

**Step 3: Modify ink.py to use custom reconciler**

The implementation involves:
1. Replace ReactPy Layout with custom Reconciler
2. Wire up `on_commit` callback to `on_render`
3. Wire up `on_compute_layout` callback
4. Handle input events with `batch_updates`

```python
# inkpy/inkpy/ink.py (key changes)

from inkpy.reconciler.reconciler import Reconciler
from inkpy.reconciler.element import Element

class Ink:
    def __init__(self, ...):
        # ... existing setup ...
        
        # Create custom reconciler instead of ReactPy Layout
        self._reconciler = Reconciler(
            on_commit=self._on_reconciler_commit,
            on_compute_layout=self.calculate_layout,
        )
    
    def render(self, node: Element) -> None:
        """Render using custom reconciler"""
        if self.is_unmounted:
            return
        
        # Wrap in App component
        from inkpy.components.app import create_app_element
        app_element = create_app_element(
            children=node,
            stdin=self.options['stdin'],
            # ... other props
        )
        
        # Render with custom reconciler
        self._reconciler.render(app_element)
    
    def _on_reconciler_commit(self, root_dom: DOMElement) -> None:
        """Called after reconciler commits changes"""
        self.root_node = root_dom
        self.on_render()
    
    async def wait_until_exit(self) -> None:
        """Wait for exit - no longer needs async render loop"""
        if self._exit_promise is None:
            self._exit_promise = asyncio.Future()
        
        return await self._exit_promise
```

**Step 4: Run test to verify it passes**
```bash
uv run pytest inkpy/tests/test_integration.py -v
```
Expected: PASS

---

## Phase 3: Port Existing Components

### Task 3.1: Port Box Component

**Files:**
- Modify: `inkpy/inkpy/components/box.py`
- Test: `inkpy/tests/components/test_box.py`

Update Box to work with custom reconciler while maintaining backward compatibility.

### Task 3.2: Port Text Component

**Files:**
- Modify: `inkpy/inkpy/components/text.py`
- Test: `inkpy/tests/components/test_text.py`

### Task 3.3: Port App Component

**Files:**
- Modify: `inkpy/inkpy/components/app.py`
- Test: `inkpy/tests/components/test_app.py`

Convert from ReactPy `@component` to custom `@component` decorator.

---

## Phase 4: Port Hooks

### Task 4.1: Port use_input Hook

**Files:**
- Modify: `inkpy/inkpy/hooks/use_input.py`
- Test: `inkpy/tests/hooks/test_use_input.py`

Key change: Use `reconciler.batch_updates()` for input handling.

### Task 4.2: Port use_app Hook

**Files:**
- Modify: `inkpy/inkpy/hooks/use_app.py`
- Test: `inkpy/tests/hooks/test_use_app.py`

### Task 4.3: Port use_focus Hook

**Files:**
- Modify: `inkpy/inkpy/hooks/use_focus.py`
- Test: `inkpy/tests/hooks/test_use_focus.py`

---

## Phase 5: Interactive Example

### Task 5.1: Update Interactive Example

**Files:**
- Modify: `inkpy/examples/interactive.py`
- Test: Manual testing

**Expected behavior:**
1. Single render on startup (no double box)
2. Arrow keys navigate selection
3. Enter on "Exit" closes app
4. Ctrl+C exits cleanly

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         InkPy Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Element    │────▶│  Reconciler  │────▶│     DOM      │    │
│  │  (create_    │     │  (fiber tree │     │  (ink-box,   │    │
│  │   element)   │     │   diffing)   │     │   ink-text)  │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                    │                    │             │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  @component  │     │    Hooks     │     │    Yoga      │    │
│  │  decorator   │     │  (use_state, │     │   Layout     │    │
│  │              │     │   use_effect)│     │              │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                              │                    │             │
│                              │                    │             │
│                              ▼                    ▼             │
│                       ┌──────────────┐     ┌──────────────┐    │
│                       │    State     │     │   Renderer   │    │
│                       │   Updates    │────▶│  (to ANSI)   │    │
│                       │  (sync!)     │     │              │    │
│                       └──────────────┘     └──────────────┘    │
│                                                   │             │
│                                                   ▼             │
│                                            ┌──────────────┐    │
│                                            │   Terminal   │    │
│                                            │   Output     │    │
│                                            └──────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

1. **Phase 1** (Core) - ~2-3 hours
   - Task 1.1: Fiber types
   - Task 1.2: Element factory
   - Task 1.3: Hooks system
   - Task 1.4: Reconciler core

2. **Phase 2** (Integration) - ~1-2 hours
   - Task 2.1: Component decorator
   - Task 2.2: Ink.py integration

3. **Phase 3** (Components) - ~2-3 hours
   - Task 3.1: Box component
   - Task 3.2: Text component
   - Task 3.3: App component

4. **Phase 4** (Hooks) - ~1-2 hours
   - Task 4.1: use_input
   - Task 4.2: use_app
   - Task 4.3: use_focus

5. **Phase 5** (Validation) - ~1 hour
   - Task 5.1: Interactive example

**Total estimated time: 7-11 hours**

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Hooks behavior differs from React | Extensive testing, reference Ink's tests |
| Performance issues with sync rendering | Add throttling similar to Ink |
| Breaking existing tests | Maintain backward compatibility layer |
| Complex diffing edge cases | Start simple, add keyed reconciliation later |

---

## Success Criteria

1. ✅ `examples/interactive.py` renders single box
2. ✅ Arrow keys change selection immediately
3. ✅ Enter on Exit closes app
4. ✅ All existing tests pass
5. ✅ State updates are synchronous (no async await needed)

---

## Next Steps

Plan saved. Ready to execute?

If yes, I will begin with Phase 1, Task 1.1 (Fiber Node Types) following TDD protocol.

