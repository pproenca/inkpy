"""
Tests for StreamingText component.

StreamingText provides incremental text rendering with:
- Typewriter effect (character by character display)
- Configurable speed
- Completion callback
- Text styling options
"""

import pytest


class TestStreamingTextImport:
    """Test StreamingText can be imported"""

    def test_streaming_text_imports(self):
        """StreamingText should be importable from components"""
        from inkpy.components.streaming_text import StreamingText

        assert StreamingText is not None
        assert callable(StreamingText)


class TestStreamingTextProps:
    """Test StreamingText prop handling"""

    def test_streaming_text_default(self):
        """StreamingText should work with just text prop"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Hello, World!")
        assert element is not None

    def test_streaming_text_with_speed(self):
        """StreamingText should accept speed_ms prop"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Hello", speed_ms=10)
        assert element is not None

    def test_streaming_text_with_callback(self):
        """StreamingText should accept on_complete callback"""
        from inkpy.components.streaming_text import StreamingText

        completed = []

        def on_complete():
            completed.append(True)

        element = StreamingText(text="Hi", on_complete=on_complete)
        assert element is not None

    def test_streaming_text_with_color(self):
        """StreamingText should accept color prop"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Hello", color="cyan")
        assert element is not None

    def test_streaming_text_with_bold(self):
        """StreamingText should accept bold prop"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Hello", bold=True)
        assert element is not None

    def test_streaming_text_with_italic(self):
        """StreamingText should accept italic prop"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Hello", italic=True)
        assert element is not None

    def test_streaming_text_combined_props(self):
        """StreamingText should accept multiple props together"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(
            text="Hello, World!",
            speed_ms=20,
            color="green",
            bold=True,
            italic=True,
            on_complete=lambda: None,
        )
        assert element is not None


class TestStreamingTextEmptyText:
    """Test StreamingText with empty or edge case text"""

    def test_streaming_text_empty_string(self):
        """StreamingText should handle empty string"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="")
        assert element is not None

    def test_streaming_text_single_char(self):
        """StreamingText should handle single character"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="X")
        assert element is not None

    def test_streaming_text_unicode(self):
        """StreamingText should handle unicode characters"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Hello 👋 World 🌍!")
        assert element is not None

    def test_streaming_text_multiline(self):
        """StreamingText should handle multiline text"""
        from inkpy.components.streaming_text import StreamingText

        element = StreamingText(text="Line 1\nLine 2\nLine 3")
        assert element is not None


class TestStreamingTextExport:
    """Test StreamingText is exported from components module"""

    def test_streaming_text_exported(self):
        """StreamingText should be exported from inkpy.components"""
        from inkpy.components import StreamingText

        assert StreamingText is not None
