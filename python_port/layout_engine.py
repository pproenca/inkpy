import poga
from typing import List, Dict, Any, Tuple

class NodeView(poga.PogaView):
    def __init__(self):
        self._children: List['NodeView'] = []
        self._layout = poga.PogaLayout(self)
        self._frame = {'x': 0, 'y': 0, 'width': 0, 'height': 0}

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
        self._frame = {'x': x, 'y': y, 'width': width, 'height': height}

    def size_that_fits(self, width: float, height: float) -> Tuple[float, float]:
        # This is for measuring text/content.
        # For now, return 0,0 or the current size.
        # In a real implementation, we'd measure text here.
        return (0, 0)

    def add_child(self, child: 'NodeView'):
        self._children.append(child)
        # We might need to notify layout about hierarchy change?
        # PogaLayout seems to handle it via __attach_nodes_from_view_hierachy__
        # but we might need to trigger it.

    def remove_child(self, child: 'NodeView'):
        if child in self._children:
            self._children.remove(child)

class YogaNode:
    def __init__(self):
        self.view = NodeView()

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
            elif key == 'align_items':
                if value == 'center':
                    layout.align_items = poga.YGAlign.Center
                elif value == 'flex-start':
                    layout.align_items = poga.YGAlign.FlexStart
                elif value == 'flex-end':
                    layout.align_items = poga.YGAlign.FlexEnd
            elif key == 'justify_content':
                if value == 'center':
                    layout.justify_content = poga.YGJustify.Center
                elif value == 'space-between':
                    layout.justify_content = poga.YGJustify.SpaceBetween
            elif key == 'padding':
                layout.padding = poga.YGValue(value, poga.YGUnit.Point)
            elif key == 'margin':
                layout.margin = poga.YGValue(value, poga.YGUnit.Point)
            # Add more mappings as needed

    def add_child(self, child: 'YogaNode'):
        self.view.add_child(child.view)

    def calculate_layout(self, width: float = None, height: float = None):
        if width is not None and height is not None:
            self.view.poga_layout().calculate_layout_with_size((width, height))
        else:
            # Maybe default to terminal size?
            self.view.poga_layout().calculate_layout_with_size((80, 24)) # Mock default

    def get_layout(self):
        # After calculate_layout, poga calls set_frame_position_and_size on the view
        # So the actual computed layout is in self.view._frame
        return self.view._frame
