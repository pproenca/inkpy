# tests/reconciler/test_hooks.py
import pytest
from inkpy.reconciler.hooks import (
    use_state,
    use_effect,
    use_context,
    use_memo,
    use_callback,
    HooksContext,
    create_context,
    ContextProvider,
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

