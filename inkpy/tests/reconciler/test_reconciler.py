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
    from inkpy.reconciler.hooks import use_state

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

