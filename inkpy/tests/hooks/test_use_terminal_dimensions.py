"""
Tests for use_terminal_dimensions hook.

use_terminal_dimensions provides access to terminal size with:
- Current columns/rows
- Updates on resize
"""

import pytest


class TestUseTerminalDimensionsImport:
    """Test use_terminal_dimensions can be imported"""

    def test_use_terminal_dimensions_imports(self):
        """use_terminal_dimensions should be importable from hooks"""
        from inkpy.hooks.use_terminal_dimensions import use_terminal_dimensions

        assert use_terminal_dimensions is not None
        assert callable(use_terminal_dimensions)


class TestUseTerminalDimensionsExport:
    """Test use_terminal_dimensions is exported from hooks module"""

    def test_use_terminal_dimensions_exported(self):
        """use_terminal_dimensions should be exported from inkpy.hooks"""
        from inkpy.hooks import use_terminal_dimensions

        assert use_terminal_dimensions is not None


class TestUseTerminalDimensionsReturn:
    """Test use_terminal_dimensions return value structure"""

    def test_returns_dict_with_columns_and_rows(self):
        """use_terminal_dimensions should return dict with columns and rows"""
        from inkpy.hooks.use_terminal_dimensions import get_terminal_dimensions

        # Test the helper function that doesn't require React context
        dimensions = get_terminal_dimensions()
        assert isinstance(dimensions, dict)
        assert "columns" in dimensions
        assert "rows" in dimensions

    def test_columns_is_integer(self):
        """columns should be an integer"""
        from inkpy.hooks.use_terminal_dimensions import get_terminal_dimensions

        dimensions = get_terminal_dimensions()
        assert isinstance(dimensions["columns"], int)
        assert dimensions["columns"] > 0

    def test_rows_is_integer(self):
        """rows should be an integer"""
        from inkpy.hooks.use_terminal_dimensions import get_terminal_dimensions

        dimensions = get_terminal_dimensions()
        assert isinstance(dimensions["rows"], int)
        assert dimensions["rows"] > 0


class TestGetTerminalDimensions:
    """Test get_terminal_dimensions utility function"""

    def test_returns_reasonable_defaults(self):
        """Should return reasonable defaults when terminal unavailable"""
        from inkpy.hooks.use_terminal_dimensions import get_terminal_dimensions

        dimensions = get_terminal_dimensions()
        # Common default terminal sizes
        assert dimensions["columns"] >= 40
        assert dimensions["rows"] >= 10
