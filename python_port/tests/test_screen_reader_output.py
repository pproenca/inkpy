"""
Tests for screen reader output mode.

Following TDD: Write failing test first, then implement.
"""
from inkpy.dom import create_node
from inkpy.renderer.screen_reader import render_node_to_screen_reader_output


def test_render_node_to_screen_reader_output_exists():
    """Test that render_node_to_screen_reader_output function exists"""
    from inkpy.renderer.screen_reader import render_node_to_screen_reader_output
    assert callable(render_node_to_screen_reader_output)


def test_screen_reader_output_skips_static_elements():
    """Test that screen reader output skips static elements when skip_static=True"""
    node = create_node('ink-box')
    node.internal_static = True
    
    output = render_node_to_screen_reader_output(node, skip_static=True)
    assert output == ''


def test_screen_reader_output_renders_text_node():
    """Test that screen reader output renders text from ink-text nodes"""
    from inkpy.dom import create_text_node, append_child_node
    
    text_node = create_node('ink-text')
    append_child_node(text_node, create_text_node("Hello"))
    append_child_node(text_node, create_text_node(" World"))
    
    output = render_node_to_screen_reader_output(text_node)
    assert output == "Hello World"


def test_screen_reader_output_uses_row_separator():
    """Test that screen reader output uses space separator for row flexDirection"""
    from inkpy.dom import create_text_node, append_child_node
    
    box = create_node('ink-box')
    box.style = {'flexDirection': 'row'}
    
    child1 = create_node('ink-text')
    append_child_node(child1, create_text_node("Hello"))
    append_child_node(box, child1)
    
    child2 = create_node('ink-text')
    append_child_node(child2, create_text_node("World"))
    append_child_node(box, child2)
    
    output = render_node_to_screen_reader_output(box)
    assert output == "Hello World"


def test_screen_reader_output_uses_column_separator():
    """Test that screen reader output uses newline separator for column flexDirection"""
    from inkpy.dom import create_text_node, append_child_node
    
    box = create_node('ink-box')
    box.style = {'flexDirection': 'column'}
    
    child1 = create_node('ink-text')
    append_child_node(child1, create_text_node("Hello"))
    append_child_node(box, child1)
    
    child2 = create_node('ink-text')
    append_child_node(child2, create_text_node("World"))
    append_child_node(box, child2)
    
    output = render_node_to_screen_reader_output(box)
    assert output == "Hello\nWorld"


def test_screen_reader_output_adds_role_annotation():
    """Test that screen reader output adds role annotation"""
    from inkpy.dom import create_text_node, append_child_node
    
    box = create_node('ink-box')
    box.internal_accessibility = {'role': 'button'}
    
    child = create_node('ink-text')
    append_child_node(child, create_text_node("Click me"))
    append_child_node(box, child)
    
    output = render_node_to_screen_reader_output(box)
    assert output == "button: Click me"


def test_screen_reader_output_adds_state_annotation():
    """Test that screen reader output adds state annotation"""
    from inkpy.dom import create_text_node, append_child_node
    
    box = create_node('ink-box')
    box.internal_accessibility = {
        'role': 'button',
        'state': {'selected': True}
    }
    
    child = create_node('ink-text')
    append_child_node(child, create_text_node("Click me"))
    append_child_node(box, child)
    
    output = render_node_to_screen_reader_output(box)
    assert "(selected) button: Click me" in output or "button: (selected) Click me" in output

