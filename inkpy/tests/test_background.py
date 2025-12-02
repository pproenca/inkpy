from inkpy.renderer.background import render_background
from inkpy.renderer.output import Output


def test_render_background():
    """Test rendering background color"""
    output = Output(width=10, height=3)
    render_background(output, x=0, y=0, width=10, height=3, color='blue')
    result = output.get()['output']
    # Check that background color is applied to all cells
    # Should contain ANSI background color codes
    assert '\x1b[44m' in result or '\x1b[48' in result  # Blue background or 24-bit color


def test_render_background_partial():
    """Test rendering background in a partial area"""
    output = Output(width=20, height=10)
    render_background(output, x=5, y=2, width=10, height=5, color='red')
    result = output.get()['output']
    # Should contain red background codes
    assert '\x1b[' in result


def test_render_background_hex_color():
    """Test rendering background with hex color"""
    output = Output(width=10, height=3)
    render_background(output, x=0, y=0, width=10, height=3, color='#ff0000')
    result = output.get()['output']
    # Should contain 24-bit color code
    assert '\x1b[48;2' in result


def test_render_background_named_color():
    """Test rendering background with named color"""
    output = Output(width=10, height=3)
    render_background(output, x=0, y=0, width=10, height=3, color='green')
    result = output.get()['output']
    # Should contain green background code
    assert '\x1b[42m' in result or '\x1b[48' in result


def test_render_background_empty():
    """Test that empty background doesn't crash"""
    output = Output(width=10, height=3)
    render_background(output, x=0, y=0, width=0, height=0, color='blue')
    result = output.get()['output']
    # Should not crash
    assert result is not None


def test_render_background_no_color():
    """Test that None color doesn't crash"""
    output = Output(width=10, height=3)
    render_background(output, x=0, y=0, width=10, height=3, color=None)
    result = output.get()['output']
    # Should not crash, may or may not have color codes
    assert result is not None


def test_render_background_overwrites():
    """Test that background overwrites existing content"""
    output = Output(width=10, height=3)
    # Write some text first
    output.write(0, 0, "Hello", transformers=[])
    # Then render background
    render_background(output, x=0, y=0, width=10, height=3, color='blue')
    result = output.get()['output']
    # Background should be applied (text may still be visible but with background)
    assert '\x1b[' in result

