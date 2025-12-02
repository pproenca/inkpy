# tests/reconciler/test_fiber.py
from inkpy.reconciler.fiber import FiberTag, create_fiber


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
