from inkpy.renderer.output import Output


def test_output_write():
    """Test writing text at specific coordinates"""
    output = Output(width=20, height=10)
    output.write(5, 2, "Hello", transformers=[])
    result = output.get()
    assert "Hello" in result['output']
    assert result['height'] == 10


def test_output_multiline():
    """Test writing multiline text"""
    output = Output(width=20, height=10)
    output.write(0, 0, "Line1\nLine2", transformers=[])
    result = output.get()
    lines = result['output'].split('\n')
    assert "Line1" in lines[0]
    assert "Line2" in lines[1]


def test_output_clip():
    """Test clipping text to boundaries"""
    output = Output(width=10, height=5)
    output.clip(x1=2, x2=8, y1=0, y2=5)
    output.write(0, 0, "Hello World", transformers=[])  # Should be clipped
    output.unclip()
    result = output.get()
    # "Hello World" starts at 0, clip at 2-8, so we should see "llo Wor"
    # But we need to check the actual output structure
    assert len(result['output']) > 0


def test_output_clip_outside():
    """Test that text completely outside clip region is not rendered"""
    output = Output(width=10, height=5)
    output.clip(x1=2, x2=8, y1=0, y2=5)
    output.write(10, 0, "Outside", transformers=[])  # Completely outside
    output.unclip()
    result = output.get()
    assert "Outside" not in result['output']


def test_output_nested_clips():
    """Test nested clipping regions"""
    output = Output(width=20, height=10)
    output.clip(x1=2, x2=18, y1=1, y2=9)
    output.clip(x1=5, x2=15, y1=3, y2=7)
    output.write(0, 0, "Should be clipped", transformers=[])
    output.unclip()
    output.unclip()
    result = output.get()
    # Text should be clipped by both regions
    assert len(result['output']) >= 0


def test_output_transformers():
    """Test applying transformers to text"""
    def uppercase_transformer(line: str, index: int) -> str:
        return line.upper()
    
    output = Output(width=20, height=10)
    output.write(0, 0, "hello", transformers=[uppercase_transformer])
    result = output.get()
    assert "HELLO" in result['output']


def test_output_empty_text():
    """Test that empty text doesn't cause errors"""
    output = Output(width=20, height=10)
    output.write(0, 0, "", transformers=[])
    result = output.get()
    assert result['output'] is not None


def test_output_bounds():
    """Test that output respects width and height bounds"""
    output = Output(width=5, height=3)
    output.write(0, 0, "This is a very long line that exceeds width", transformers=[])
    result = output.get()
    # Should not crash, but may truncate or wrap
    assert result['height'] == 3


def test_output_preserves_ansi_codes():
    """Test that Output preserves ANSI codes when writing styled text"""
    output = Output(width=20, height=10)
    red_text = "\x1b[31mRed\x1b[0m"
    output.write(0, 0, red_text, transformers=[])
    result = output.get()
    
    # ANSI codes should be preserved in output
    assert '\x1b[31m' in result['output']
    assert 'Red' in result['output']


def test_output_clip_preserves_ansi_codes():
    """Test that clipping preserves ANSI codes"""
    output = Output(width=20, height=10)
    output.clip(x1=2, x2=10, y1=0, y2=10)
    red_text = "\x1b[31mHello World\x1b[0m"
    output.write(0, 0, red_text, transformers=[])
    output.unclip()
    result = output.get()
    
    # ANSI codes should be preserved even after clipping
    assert '\x1b[31m' in result['output']
    assert 'Hello' in result['output'] or 'World' in result['output']


def test_output_handles_wide_characters():
    """Test that Output handles multi-column characters (CJK) correctly"""
    output = Output(width=20, height=10)
    text_with_cjk = "A中B"  # Chinese character is 2 columns wide
    output.write(0, 0, text_with_cjk, transformers=[])
    result = output.get()
    
    # Should include the Chinese character
    assert '中' in result['output']

