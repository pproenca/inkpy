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

    HOST_ROOT = auto()  # Root of the fiber tree
    HOST_COMPONENT = auto()  # DOM element (ink-box, ink-text)
    FUNCTION_COMPONENT = auto()  # Function component
    CLASS_COMPONENT = auto()  # Class component (for future use)
    TEXT_NODE = auto()  # Text content


class EffectTag(IntEnum):
    """Side effect tags for commit phase"""

    NONE = 0
    PLACEMENT = 1  # New node to insert
    UPDATE = 2  # Node needs update
    DELETION = 4  # Node to remove
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
    child: Optional["FiberNode"] = None
    sibling: Optional["FiberNode"] = None
    parent: Optional["FiberNode"] = None  # 'return' in React
    index: int = 0

    # DOM reference
    dom: Any = None  # DOMElement or TextNode

    # Double buffering
    alternate: Optional["FiberNode"] = None

    # Effects
    effect_tag: EffectTag = EffectTag.NONE
    effects: List["FiberNode"] = field(default_factory=list)

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

