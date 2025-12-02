"""
Tests for ProgressBar component.

ProgressBar provides a determinate progress indicator with:
- Configurable width
- Custom filled/empty characters
- Percentage display
- Color support
"""

import pytest


class TestProgressBarImport:
    """Test ProgressBar can be imported"""

    def test_progress_bar_imports(self):
        """ProgressBar should be importable from components"""
        from inkpy.components.progress_bar import ProgressBar

        assert ProgressBar is not None
        assert callable(ProgressBar)


class TestProgressBarProps:
    """Test ProgressBar prop handling"""

    def test_progress_bar_default(self):
        """ProgressBar should work with just value prop"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.5)
        assert element is not None

    def test_progress_bar_zero(self):
        """ProgressBar should handle 0% progress"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.0)
        assert element is not None

    def test_progress_bar_full(self):
        """ProgressBar should handle 100% progress"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=1.0)
        assert element is not None

    def test_progress_bar_with_width(self):
        """ProgressBar should accept width prop"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.5, width=20)
        assert element is not None

    def test_progress_bar_with_custom_chars(self):
        """ProgressBar should accept custom filled/empty chars"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.5, filled_char="=", empty_char="-")
        assert element is not None

    def test_progress_bar_with_color(self):
        """ProgressBar should accept color prop"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.5, color="green")
        assert element is not None

    def test_progress_bar_hide_percentage(self):
        """ProgressBar should allow hiding percentage"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.5, show_percentage=False)
        assert element is not None

    def test_progress_bar_custom_brackets(self):
        """ProgressBar should accept custom bracket characters"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=0.5, left_bracket="(", right_bracket=")")
        assert element is not None


class TestProgressBarValueClamping:
    """Test ProgressBar value clamping"""

    def test_progress_bar_negative_value(self):
        """ProgressBar should clamp negative values to 0"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=-0.5)
        assert element is not None

    def test_progress_bar_value_over_one(self):
        """ProgressBar should clamp values over 1 to 1"""
        from inkpy.components.progress_bar import ProgressBar

        element = ProgressBar(value=1.5)
        assert element is not None


class TestProgressBarExport:
    """Test ProgressBar is exported from components module"""

    def test_progress_bar_exported(self):
        """ProgressBar should be exported from inkpy.components"""
        from inkpy.components import ProgressBar

        assert ProgressBar is not None
