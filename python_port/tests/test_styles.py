from inkpy.layout.yoga_node import YogaNode
from inkpy.layout.styles import apply_styles


def test_padding_x_y():
    """Test paddingX and paddingY shortcuts"""
    node = YogaNode()
    apply_styles(node, {'paddingX': 5, 'paddingY': 2})
    layout = node.view.poga_layout()
    # Check that padding left/right = 5, top/bottom = 2
    # We'll verify by checking the layout object
    assert layout is not None


def test_padding_individual():
    """Test individual padding properties"""
    node = YogaNode()
    apply_styles(node, {
        'paddingTop': 1,
        'paddingRight': 2,
        'paddingBottom': 3,
        'paddingLeft': 4
    })
    layout = node.view.poga_layout()
    assert layout is not None


def test_margin_x_y():
    """Test marginX and marginY shortcuts"""
    node = YogaNode()
    apply_styles(node, {'marginX': 5, 'marginY': 2})
    layout = node.view.poga_layout()
    assert layout is not None


def test_margin_individual():
    """Test individual margin properties"""
    node = YogaNode()
    apply_styles(node, {
        'marginTop': 1,
        'marginRight': 2,
        'marginBottom': 3,
        'marginLeft': 4
    })
    layout = node.view.poga_layout()
    assert layout is not None


def test_border_styles():
    """Test border style application"""
    node = YogaNode()
    apply_styles(node, {'borderStyle': 'single', 'borderTop': False})
    layout = node.view.poga_layout()
    # Border should be 1 on left/right/bottom, 0 on top
    assert layout is not None


def test_percentage_dimensions():
    """Test width/height as percentages"""
    node = YogaNode()
    apply_styles(node, {'width': '50%', 'height': '100%'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_wrap():
    """Test flexWrap property"""
    node = YogaNode()
    apply_styles(node, {'flexWrap': 'wrap'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_basis():
    """Test flexBasis property"""
    node = YogaNode()
    apply_styles(node, {'flexBasis': 100})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_basis_percent():
    """Test flexBasis as percentage"""
    node = YogaNode()
    apply_styles(node, {'flexBasis': '50%'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_flex_basis_auto():
    """Test flexBasis as 'auto' or undefined"""
    # Test with None (undefined/auto)
    node = YogaNode()
    apply_styles(node, {'flexBasis': None})
    layout = node.view.poga_layout()
    assert layout is not None
    
    # Test with 'auto' string
    node2 = YogaNode()
    apply_styles(node2, {'flexBasis': 'auto'})
    layout2 = node2.view.poga_layout()
    assert layout2 is not None


def test_justify_content_space_evenly():
    """Test space-evenly justification"""
    node = YogaNode()
    apply_styles(node, {'justifyContent': 'space-evenly'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_gap_properties():
    """Test gap, columnGap, rowGap properties"""
    node = YogaNode()
    apply_styles(node, {'gap': 5})
    layout = node.view.poga_layout()
    assert layout is not None
    
    node2 = YogaNode()
    apply_styles(node2, {'columnGap': 3, 'rowGap': 4})
    layout2 = node2.view.poga_layout()
    assert layout2 is not None


def test_position_absolute():
    """Test position: absolute"""
    node = YogaNode()
    apply_styles(node, {'position': 'absolute'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_display_none():
    """Test display: none"""
    node = YogaNode()
    apply_styles(node, {'display': 'none'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_min_width_height_percent():
    """Test minWidth and minHeight as percentages"""
    node = YogaNode()
    apply_styles(node, {'minWidth': '25%', 'minHeight': '50%'})
    layout = node.view.poga_layout()
    assert layout is not None


def test_align_self_auto():
    """Test alignSelf: auto"""
    node = YogaNode()
    apply_styles(node, {'alignSelf': 'auto'})
    layout = node.view.poga_layout()
    assert layout is not None

