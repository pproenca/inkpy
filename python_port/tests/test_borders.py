import pytest
from inkpy.renderer.borders import get_border_chars, render_border
from inkpy.renderer.output import Output


def test_single_border():
    """Test single border character set"""
    border = get_border_chars('single')
    assert border['topLeft'] == '┌'
    assert border['horizontal'] == '─'
    assert border['vertical'] == '│'
    assert border['topRight'] == '┐'
    assert border['bottomLeft'] == '└'
    assert border['bottomRight'] == '┘'
    assert border['top'] == '─'
    assert border['bottom'] == '─'
    assert border['left'] == '│'
    assert border['right'] == '│'


def test_double_border():
    """Test double border character set"""
    border = get_border_chars('double')
    assert border['topLeft'] == '╔'
    assert border['horizontal'] == '═'
    assert border['vertical'] == '║'


def test_round_border():
    """Test round border character set"""
    border = get_border_chars('round')
    assert border['topLeft'] == '╭'
    assert border['topRight'] == '╮'
    assert border['bottomLeft'] == '╰'
    assert border['bottomRight'] == '╯'


def test_bold_border():
    """Test bold border character set"""
    border = get_border_chars('bold')
    assert border['topLeft'] == '┏'
    assert border['horizontal'] == '━'
    assert border['vertical'] == '┃'


def test_render_box_with_border():
    """Test rendering a box with border"""
    output = Output(width=10, height=5)
    render_border(output, x=0, y=0, width=10, height=5, style='single')
    result = output.get()['output']
    assert '┌' in result  # Top-left corner
    assert '┐' in result  # Top-right corner
    assert '└' in result  # Bottom-left corner
    assert '┘' in result  # Bottom-right corner


def test_render_border_partial():
    """Test rendering border with some sides hidden"""
    output = Output(width=10, height=5)
    render_border(
        output, x=0, y=0, width=10, height=5,
        style='single',
        borderTop=False,
        borderBottom=True,
        borderLeft=True,
        borderRight=True
    )
    result = output.get()['output']
    assert '┌' not in result  # Top-left should not be there
    assert '└' in result  # Bottom-left should be there


def test_render_border_colored():
    """Test rendering colored border"""
    output = Output(width=10, height=5)
    render_border(
        output, x=0, y=0, width=10, height=5,
        style='single',
        borderColor='red'
    )
    result = output.get()['output']
    # Should contain ANSI color codes
    assert '\x1b[' in result


def test_invalid_border_style():
    """Test that invalid border style returns default"""
    border = get_border_chars('invalid')
    # Should return single as default
    assert border['topLeft'] == '┌'

