"""
Reconciler - The core of the custom component system.

Implements a simplified React Fiber reconciler that:
1. Builds a fiber tree from elements
2. Reconciles changes (diffing)
3. Commits changes to DOM
4. Handles state updates synchronously
"""
from typing import Any, Callable, Optional, List, Dict, Union
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
        
        # Track current element for re-renders
        self._current_element: Optional[Element] = None

    def render(self, element: Element) -> None:
        """
        Render an element tree.

        This is the entry point - creates or updates the fiber tree
        and commits changes to DOM.
        """
        # Store current element for re-renders
        self._current_element = element
        
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
        if self._needs_render and self._current_element:
            self.render(self._current_element)
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
            old_props = fiber.alternate.props if fiber.alternate else {}
            self._update_dom(fiber.dom, old_props, fiber.props)

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
        dom,
        old_props: Dict,
        new_props: Dict
    ) -> None:
        """Update DOM node properties"""
        from inkpy.dom import TextNode, set_text_node_value
        
        # Handle text nodes specially
        if isinstance(dom, TextNode):
            new_text = new_props.get("text", "")
            if dom.node_value != new_text:
                set_text_node_value(dom, new_text)
            return
        
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

