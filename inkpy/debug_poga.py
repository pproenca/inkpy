import poga


class MyView(poga.PogaView):
    def __init__(self, name="View"):
        self.name = name
        self.children = []
        self.layout = poga.PogaLayout(self)
        self.frame = {"x": 0, "y": 0, "width": 0, "height": 0}

    def poga_layout(self):
        return self.layout

    def subviews(self):
        return self.children

    def subviews_count(self):
        return len(self.children)

    def is_container(self):
        return True

    def set_frame_position_and_size(self, x, y, w, h):
        # print(f"{self.name}: set_frame x={x} y={y} w={w} h={h}")
        self.frame = {"x": x, "y": y, "width": w, "height": h}

    def bounds_size(self):
        return (self.frame["width"], self.frame["height"])

    def frame_origin(self):
        return (self.frame["x"], self.frame["y"])

    def size_that_fits(self, w, h):
        return (0, 0)


def test():
    root = MyView("Root")
    root.layout.width = poga.YGValue(100, poga.YGUnit.Point)
    root.layout.height = poga.YGValue(100, poga.YGUnit.Point)
    root.layout.flex_direction = poga.YGFlexDirection.Row
    # root.layout.align_items = poga.YGAlign.Center

    child = MyView("Child")
    child.layout.width = poga.YGValue(20, poga.YGUnit.Point)
    child.layout.height = poga.YGValue(20, poga.YGUnit.Point)
    child.layout.align_self = poga.YGAlign.Center

    root.children.append(child)

    poga.PogaLayout.__attach_nodes_from_view_hierachy__(root)

    root.layout.calculate_layout_with_size((100, 100))

    poga.PogaLayout.__apply_layout_to_view_hierarchy__(root, False)

    print(f"Root: {root.frame}")
    print(f"Child: {child.frame}")

    if child.frame["y"] == 40:
        print("SUCCESS: Child centered vertically via align_self")
    else:
        print(f"FAILURE: Child not centered. y={child.frame['y']}")


if __name__ == "__main__":
    test()
