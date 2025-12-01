import poga
from typing import List, Dict, Any, Tuple, Optional

class NodeView(poga.PogaView):
    def __init__(self):
        self._children: List['NodeView'] = []
        self._layout = poga.PogaLayout(self)
        self._frame = {'x': 0.0, 'y': 0.0, 'width': 0.0, 'height': 0.0}

    def poga_layout(self) -> poga.PogaLayout:
        return self._layout

    def subviews(self) -> List['NodeView']:
        return self._children

    def subviews_count(self) -> int:
        return len(self._children)

    def is_container(self) -> bool:
        return True

    def bounds_size(self) -> Tuple[float, float]:
        return (self._frame['width'], self._frame['height'])

    def frame_origin(self) -> Tuple[float, float]:
        return (self._frame['x'], self._frame['y'])

    def set_frame_position_and_size(self, x: float, y: float, width: float, height: float):
        # Poga seems to set position relative to parent content box? Or margin box?
        # Debugging showed 0,0 often.

        # In standard Yoga, layout.left/top are relative to parent.
        # Poga's set_frame_position_and_size might be called with absolute coords or relative?
        # Looking at PogaLayout source:
        # view.set_frame_position_and_size(
        #    PogaLayout.__round_pixel_value__(left_top[0] + origin[0]),
        #    PogaLayout.__round_pixel_value__(left_top[1] + origin[1]),
        #    ...

        # It adds origin. If origin is 0,0, it sets left/top.
        # However, for subviews, it seems to be traversing recursively.

        # IMPORTANT: The issue might be that we're not using a "Host" view mechanism that some systems expect?
        # Or maybe the frame needs to be accumulated?

        self._frame = {'x': x, 'y': y, 'width': width, 'height': height}

    def size_that_fits(self, width: float, height: float) -> Tuple[float, float]:
        # Check if there's a measure function set (for text nodes)
        if hasattr(self, '_measure_func') and self._measure_func:
            result = self._measure_func(width, height)
            # Convert dict to tuple if needed
            if isinstance(result, dict):
                return (result.get('width', 0.0), result.get('height', 0.0))
            elif isinstance(result, tuple):
                return result
            else:
                return (float(result.get('width', 0)), float(result.get('height', 0)))
        return (0, 0)

    def add_child(self, child: 'NodeView'):
        self._children.append(child)
        # We need to make sure the layout engine knows about the new child
        # Usually this happens when calculate_layout is called, as poga traverses the view hierarchy

    def remove_child(self, child: 'NodeView'):
        if child in self._children:
            self._children.remove(child)

class YogaNode:
    def __init__(self):
        self.view = NodeView()
        self.children: List['YogaNode'] = []
        # Set default styles to match Ink/standard behavior
        # Ink defaults to column layout
        self.view.poga_layout().flex_direction = poga.YGFlexDirection.Column
        # Standard Yoga/Flexbox default for align_items is Stretch, but in Poga/Ink it might differ.
        # Ink documentation says: "alignItems: 'stretch' (default)"
        self.view.poga_layout().align_items = poga.YGAlign.Stretch
        self.view.poga_layout().justify_content = poga.YGJustify.FlexStart

        # Ensure flex shrink is 1 by default (standard)
        self.view.poga_layout().flex_shrink = 1

        # Ensure display is flex
        # self.view.poga_layout().display = poga.YGDisplay.Flex

    def set_style(self, style: Dict[str, Any]):
        layout = self.view.poga_layout()
        for key, value in style.items():
            if key == 'width':
                layout.width = poga.YGValue(value, poga.YGUnit.Point)
            elif key == 'height':
                layout.height = poga.YGValue(value, poga.YGUnit.Point)
            elif key == 'min_width':
                layout.min_width = poga.YGValue(value, poga.YGUnit.Point)
            elif key == 'min_height':
                layout.min_height = poga.YGValue(value, poga.YGUnit.Point)
            elif key == 'flex_grow':
                layout.flex_grow = value
            elif key == 'flex_shrink':
                layout.flex_shrink = value
            elif key == 'flex_direction':
                if value == 'row':
                    layout.flex_direction = poga.YGFlexDirection.Row
                elif value == 'column':
                    layout.flex_direction = poga.YGFlexDirection.Column
                elif value == 'row-reverse':
                    layout.flex_direction = poga.YGFlexDirection.RowReverse
                elif value == 'column-reverse':
                    layout.flex_direction = poga.YGFlexDirection.ColumnReverse
            elif key == 'align_items':
                if value == 'center':
                    layout.align_items = poga.YGAlign.Center
                elif value == 'flex-start':
                    layout.align_items = poga.YGAlign.FlexStart
                elif value == 'flex-end':
                    layout.align_items = poga.YGAlign.FlexEnd
                elif value == 'stretch':
                    layout.align_items = poga.YGAlign.Stretch
            elif key == 'align_self':
                if value == 'center':
                    layout.align_self = poga.YGAlign.Center
                elif value == 'flex-start':
                    layout.align_self = poga.YGAlign.FlexStart
                elif value == 'flex-end':
                    layout.align_self = poga.YGAlign.FlexEnd
                elif value == 'stretch':
                    layout.align_self = poga.YGAlign.Stretch
            elif key == 'justify_content':
                if value == 'center':
                    layout.justify_content = poga.YGJustify.Center
                elif value == 'flex-start':
                    layout.justify_content = poga.YGJustify.FlexStart
                elif value == 'flex-end':
                    layout.justify_content = poga.YGJustify.FlexEnd
                elif value == 'space-between':
                    layout.justify_content = poga.YGJustify.SpaceBetween
                elif value == 'space-around':
                    layout.justify_content = poga.YGJustify.SpaceAround
            elif key == 'padding':
                layout.padding = poga.YGValue(value, poga.YGUnit.Point)
            elif key == 'margin':
                layout.margin = poga.YGValue(value, poga.YGUnit.Point)

            # Add more exhaustive mappings as needed

    def add_child(self, child: 'YogaNode'):
        self.children.append(child)
        self.view.add_child(child.view)

    def remove_child(self, child: 'YogaNode'):
        if child in self.children:
            self.children.remove(child)
            self.view.remove_child(child.view)

    def calculate_layout(self, width: Optional[float] = None, height: Optional[float] = None):
        w = width if width is not None else poga.YGUndefined
        h = height if height is not None else poga.YGUndefined

        # Sync view hierarchy
        poga.PogaLayout.__attach_nodes_from_view_hierachy__(self.view)

        # Set direction explicitly
        self.view.poga_layout().direction = poga.YGDirection.LTR

        # Calculate layout
        self.view.poga_layout().calculate_layout_with_size((w, h))

        # Apply results recursively
        # We MUST pass preserve_origin=False to ensure x/y are updated from layout logic
        poga.PogaLayout.__apply_layout_to_view_hierarchy__(self.view, False)

        # DEBUG: Traverse and print frames
        # self._debug_print_frames(self, 0)

    def _debug_print_frames(self, node, depth):
        indent = "  " * depth
        # print(f"{indent}{node.view._frame}")
        for child in node.children:
            self._debug_print_frames(child, depth + 1)

    def get_layout(self) -> Dict[str, float]:
        # Return layout compatible with Ink/tests
        # left, top, width, height

        # If the view frame is not what we expect, we can try to pull directly from the layout node
        # But we shouldn't need to rely on private access.

        # One edge case: poga might not be updating the frame if the node is the root?
        # But children are not roots.

        # Let's just trust the frame for now, assuming calculate_layout updated it.
        return {
            'left': self.view._frame['x'],
            'top': self.view._frame['y'],
            'width': self.view._frame['width'],
            'height': self.view._frame['height']
        }
    
    def get_computed_width(self) -> float:
        """Get computed width of the node (matches TypeScript getComputedWidth)"""
        return self.get_layout().get('width', 0.0)
    
    def get_computed_height(self) -> float:
        """Get computed height of the node (matches TypeScript getComputedHeight)"""
        return self.get_layout().get('height', 0.0)
