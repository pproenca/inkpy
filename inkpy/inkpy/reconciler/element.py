"""
Element - Immutable description of what to render.

Similar to React.createElement() - creates element descriptors
that the reconciler uses to build the fiber tree.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Union


@dataclass(frozen=True)
class Element:
    """
    An immutable element descriptor.

    Elements describe what should be rendered but don't contain
    any state or lifecycle - that's handled by fibers.
    """

    type: Union[str, Callable]  # "ink-box" or component function
    props: dict[str, Any]
    key: Optional[str] = None


def create_element(
    element_type: Union[str, Callable],
    props: Optional[dict[str, Any]] = None,
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
