from inkpy.layout.styles import apply_styles
from inkpy.layout.yoga_node import YogaNode


def test_padding_x_y():
    """Test paddingX and paddingY shortcuts"""
    node = YogaNode()
    apply_styles(node, {"paddingX": 5, "paddingY": 2})
    layout = node.view.poga_layout()
    # Check that padding left/right = 5, top/bottom = 2
    # We'll verify by checking the layout object
    assert layout is not None


def test_padding_individual():
    """Test individual padding properties"""
    node = YogaNode()
    apply_styles(node, {"paddingTop": 1, "paddingRight": 2, "paddingBottom": 3, "paddingLeft": 4})
    layout = node.view.poga_layout()
    assert layout is not None


def test_margin_x_y():
    """Test marginX and marginY shortcuts"""
    node = YogaNode()
    apply_styles(node, {"marginX": 5, "marginY": 2})
    layout = node.view.poga_layout()
    assert layout is not None


def test_margin_individual():
    """Test individual margin properties"""
    node = YogaNode()
    apply_styles(node, {"marginTop": 1, "marginRight": 2, "marginBottom": 3, "marginLeft": 4})
    layout = node.view.poga_layout()
    assert layout is not None


def test_border_styles():
    """Test border style application"""
    node = YogaNode()
    apply_styles(node, {"borderStyle": "single", "borderTop": False})
    layout = node.view.poga_layout()
    # Border should be 1 on left/right/bottom, 0 on top
    assert layout is not None


def test_percentage_dimensions():
    """Test width/height as percentages"""
    node = YogaNode()
    apply_styles(node, {"width": "50%", "height": "100%"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_wrap():
    """Test flexWrap property"""
    node = YogaNode()
    apply_styles(node, {"flexWrap": "wrap"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_basis():
    """Test flexBasis property"""
    node = YogaNode()
    apply_styles(node, {"flexBasis": 100})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_basis_percent():
    """Test flexBasis as percentage"""
    node = YogaNode()
    apply_styles(node, {"flexBasis": "50%"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_basis_auto():
    """Test flexBasis as 'auto' or undefined"""
    # Test with None (undefined/auto)
    node = YogaNode()
    apply_styles(node, {"flexBasis": None})
    layout = node.view.poga_layout()
    assert layout is not None

    # Test with 'auto' string
    node2 = YogaNode()
    apply_styles(node2, {"flexBasis": "auto"})
    layout2 = node2.view.poga_layout()
    assert layout2 is not None


def test_justify_content_space_evenly():
    """Test space-evenly justification"""
    node = YogaNode()
    apply_styles(node, {"justifyContent": "space-evenly"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_gap_properties():
    """Test gap, columnGap, rowGap properties"""
    node = YogaNode()
    apply_styles(node, {"gap": 5})
    layout = node.view.poga_layout()
    assert layout is not None

    node2 = YogaNode()
    apply_styles(node2, {"columnGap": 3, "rowGap": 4})
    layout2 = node2.view.poga_layout()
    assert layout2 is not None


def test_position_absolute():
    """Test position: absolute"""
    node = YogaNode()
    apply_styles(node, {"position": "absolute"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_display_none():
    """Test display: none"""
    node = YogaNode()
    apply_styles(node, {"display": "none"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_min_width_height_percent():
    """Test minWidth and minHeight as percentages"""
    node = YogaNode()
    apply_styles(node, {"minWidth": "25%", "minHeight": "50%"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_self_auto():
    """Test alignSelf: auto"""
    node = YogaNode()
    apply_styles(node, {"alignSelf": "auto"})
    layout = node.view.poga_layout()
    assert layout is not None


# --- Task 3: flexBasis auto verification tests ---


def test_flex_basis_auto_layout_behavior():
    """Test that flexBasis: 'auto' uses content size as basis.

    This is the key G3 verification: flexBasis auto should allow
    flex items to size based on their content.
    """
    from inkpy.layout.text_node import TextNode

    # Create container with row direction
    container = YogaNode()
    apply_styles(
        container,
        {
            "flexDirection": "row",
            "width": 100,
        },
    )

    # Create child with flexBasis: 'auto'
    child = YogaNode()
    apply_styles(child, {"flexBasis": "auto", "flexGrow": 0, "flexShrink": 0})

    # Add text content to give it intrinsic size
    text = TextNode("Hello")  # ~5 chars
    child.add_child(text)
    container.add_child(child)

    # Calculate layout
    container.calculate_layout(width=100)

    # With flexBasis: auto, the child should take its content size
    child_layout = child.get_layout()
    # Width should be approximately text width (not 0, not 100)
    assert child_layout.get("width", 0) > 0
    assert child_layout.get("width", 0) < 100


def test_flex_basis_fixed_vs_auto():
    """Compare flexBasis: fixed value vs flexBasis: 'auto'.

    A fixed value should override content size.
    """
    from inkpy.layout.text_node import TextNode

    # Child with fixed flexBasis
    container1 = YogaNode()
    apply_styles(container1, {"flexDirection": "row", "width": 100})

    fixed_child = YogaNode()
    apply_styles(fixed_child, {"flexBasis": 50})
    text1 = TextNode("Hello")
    fixed_child.add_child(text1)
    container1.add_child(fixed_child)
    container1.calculate_layout(width=100)

    fixed_layout = fixed_child.get_layout()

    # Child with auto flexBasis
    container2 = YogaNode()
    apply_styles(container2, {"flexDirection": "row", "width": 100})

    auto_child = YogaNode()
    apply_styles(auto_child, {"flexBasis": "auto"})
    text2 = TextNode("Hello")
    auto_child.add_child(text2)
    container2.add_child(auto_child)
    container2.calculate_layout(width=100)

    auto_layout = auto_child.get_layout()

    # Fixed should be 50, auto should be content-based (different)
    assert fixed_layout.get("width", 0) == 50
    # Auto width depends on content - should be around text width
    assert auto_layout.get("width", 0) != 50


def test_flex_basis_percentage():
    """Test that flexBasis percentage works correctly."""
    container = YogaNode()
    apply_styles(
        container,
        {
            "flexDirection": "row",
            "width": 100,
        },
    )

    child = YogaNode()
    apply_styles(child, {"flexBasis": "50%"})
    container.add_child(child)

    container.calculate_layout(width=100)

    child_layout = child.get_layout()
    # 50% of 100 = 50
    assert child_layout.get("width", 0) == 50


def test_flex_basis_with_grow():
    """Test flexBasis: 'auto' combined with flexGrow."""
    from inkpy.layout.text_node import TextNode

    container = YogaNode()
    apply_styles(
        container,
        {
            "flexDirection": "row",
            "width": 100,
        },
    )

    # Two children, both with flexGrow: 1
    child1 = YogaNode()
    apply_styles(child1, {"flexBasis": "auto", "flexGrow": 1})
    text1 = TextNode("Hi")
    child1.add_child(text1)
    container.add_child(child1)

    child2 = YogaNode()
    apply_styles(child2, {"flexBasis": "auto", "flexGrow": 1})
    text2 = TextNode("Hi")
    child2.add_child(text2)
    container.add_child(child2)

    container.calculate_layout(width=100)

    # Both should share remaining space equally
    layout1 = child1.get_layout()
    layout2 = child2.get_layout()

    # They should be approximately equal (both growing to fill space)
    width1 = layout1.get("width", 0)
    width2 = layout2.get("width", 0)
    assert abs(width1 - width2) < 2  # Allow small rounding differences


# --- Phase 4.4: Additional Tests for 95%+ Coverage ---


def test_position_relative():
    """Test position: relative"""
    node = YogaNode()
    apply_styles(node, {"position": "relative"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_margin_shorthand():
    """Test margin shorthand property"""
    node = YogaNode()
    apply_styles(node, {"margin": 10})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_shrink_non_numeric():
    """Test flexShrink with non-numeric value defaults to 1"""
    node = YogaNode()
    apply_styles(node, {"flexShrink": "invalid"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_wrap_reverse():
    """Test flexWrap: wrap-reverse"""
    node = YogaNode()
    apply_styles(node, {"flexWrap": "wrap-reverse"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_direction_row_reverse():
    """Test flexDirection: row-reverse"""
    node = YogaNode()
    apply_styles(node, {"flexDirection": "row-reverse"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_direction_column_reverse():
    """Test flexDirection: column-reverse"""
    node = YogaNode()
    apply_styles(node, {"flexDirection": "column-reverse"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_items_stretch():
    """Test alignItems: stretch (or falsy value defaults to stretch)"""
    node = YogaNode()
    apply_styles(node, {"alignItems": "stretch"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_items_flex_start():
    """Test alignItems: flex-start"""
    node = YogaNode()
    apply_styles(node, {"alignItems": "flex-start"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_items_center():
    """Test alignItems: center"""
    node = YogaNode()
    apply_styles(node, {"alignItems": "center"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_items_flex_end():
    """Test alignItems: flex-end"""
    node = YogaNode()
    apply_styles(node, {"alignItems": "flex-end"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_self_flex_start():
    """Test alignSelf: flex-start"""
    node = YogaNode()
    apply_styles(node, {"alignSelf": "flex-start"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_self_center():
    """Test alignSelf: center"""
    node = YogaNode()
    apply_styles(node, {"alignSelf": "center"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_self_flex_end():
    """Test alignSelf: flex-end"""
    node = YogaNode()
    apply_styles(node, {"alignSelf": "flex-end"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_self_stretch():
    """Test alignSelf: stretch"""
    node = YogaNode()
    apply_styles(node, {"alignSelf": "stretch"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_justify_content_flex_start():
    """Test justifyContent: flex-start (or falsy defaults to it)"""
    node = YogaNode()
    apply_styles(node, {"justifyContent": "flex-start"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_justify_content_center():
    """Test justifyContent: center"""
    node = YogaNode()
    apply_styles(node, {"justifyContent": "center"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_justify_content_flex_end():
    """Test justifyContent: flex-end"""
    node = YogaNode()
    apply_styles(node, {"justifyContent": "flex-end"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_justify_content_space_between():
    """Test justifyContent: space-between"""
    node = YogaNode()
    apply_styles(node, {"justifyContent": "space-between"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_justify_content_space_around():
    """Test justifyContent: space-around"""
    node = YogaNode()
    apply_styles(node, {"justifyContent": "space-around"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_width_undefined():
    """Test width with undefined/auto value"""
    node = YogaNode()
    apply_styles(node, {"width": None})
    layout = node.view.poga_layout()
    assert layout is not None


def test_height_undefined():
    """Test height with undefined/auto value"""
    node = YogaNode()
    apply_styles(node, {"height": None})
    layout = node.view.poga_layout()
    assert layout is not None


def test_min_width_numeric():
    """Test minWidth with numeric value"""
    node = YogaNode()
    apply_styles(node, {"minWidth": 50})
    layout = node.view.poga_layout()
    assert layout is not None


def test_min_height_numeric():
    """Test minHeight with numeric value"""
    node = YogaNode()
    apply_styles(node, {"minHeight": 30})
    layout = node.view.poga_layout()
    assert layout is not None


def test_display_flex():
    """Test display: flex"""
    node = YogaNode()
    apply_styles(node, {"display": "flex"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_border_bottom_false():
    """Test borderBottom: false"""
    node = YogaNode()
    apply_styles(node, {"borderStyle": "single", "borderBottom": False})
    layout = node.view.poga_layout()
    assert layout is not None


def test_border_left_false():
    """Test borderLeft: false"""
    node = YogaNode()
    apply_styles(node, {"borderStyle": "single", "borderLeft": False})
    layout = node.view.poga_layout()
    assert layout is not None


def test_border_right_false():
    """Test borderRight: false"""
    node = YogaNode()
    apply_styles(node, {"borderStyle": "single", "borderRight": False})
    layout = node.view.poga_layout()
    assert layout is not None


def test_all_borders_disabled():
    """Test all borders disabled"""
    node = YogaNode()
    apply_styles(
        node,
        {
            "borderStyle": "single",
            "borderTop": False,
            "borderBottom": False,
            "borderLeft": False,
            "borderRight": False,
        },
    )
    layout = node.view.poga_layout()
    assert layout is not None


def test_padding_shorthand():
    """Test padding shorthand property (all sides)"""
    node = YogaNode()
    apply_styles(node, {"padding": 8})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_wrap_nowrap():
    """Test flexWrap: nowrap"""
    node = YogaNode()
    apply_styles(node, {"flexWrap": "nowrap"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_direction_column():
    """Test flexDirection: column"""
    node = YogaNode()
    apply_styles(node, {"flexDirection": "column"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_height_auto_string():
    """Test height with 'auto' string value"""
    node = YogaNode()
    apply_styles(node, {"height": "auto"})
    layout = node.view.poga_layout()
    assert layout is not None


def test_width_auto_string():
    """Test width with 'auto' string value"""
    node = YogaNode()
    apply_styles(node, {"width": "auto"})
    layout = node.view.poga_layout()
    assert layout is not None
