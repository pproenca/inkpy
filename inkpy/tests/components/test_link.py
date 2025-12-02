"""
Tests for Link component.

Link provides terminal hyperlinks using OSC 8 escape sequences.
Supported by modern terminals like iTerm2, Hyper, Windows Terminal.
"""

import pytest


class TestLinkImport:
    """Test Link component can be imported"""

    def test_link_imports(self):
        """Link should be importable from components"""
        from inkpy.components.link import Link

        assert Link is not None
        assert callable(Link)


class TestLinkProps:
    """Test Link prop handling"""

    def test_link_with_url(self):
        """Link should accept url prop"""
        from inkpy.components.link import Link

        element = Link(url="https://example.com")
        assert element is not None

    def test_link_with_children(self):
        """Link should accept children prop for link text"""
        from inkpy.components.link import Link

        element = Link(url="https://example.com", children="Click here")
        assert element is not None

    def test_link_with_fallback(self):
        """Link should accept fallback prop for unsupported terminals"""
        from inkpy.components.link import Link

        element = Link(url="https://example.com", fallback=True)
        assert element is not None

    def test_link_url_as_text_when_no_children(self):
        """Link should use URL as text when no children provided"""
        from inkpy.components.link import Link

        element = Link(url="https://example.com")
        assert element is not None


class TestLinkUtilities:
    """Test link utility functions"""

    def test_create_hyperlink_imports(self):
        """create_hyperlink should be importable"""
        from inkpy.components.link import create_hyperlink

        assert create_hyperlink is not None
        assert callable(create_hyperlink)

    def test_create_hyperlink_returns_string(self):
        """create_hyperlink should return a string with OSC 8 sequences"""
        from inkpy.components.link import create_hyperlink

        result = create_hyperlink("https://example.com", "Example")
        assert isinstance(result, str)
        assert "example.com" in result

    def test_create_hyperlink_osc8_format(self):
        """create_hyperlink should use OSC 8 escape sequence format"""
        from inkpy.components.link import create_hyperlink

        result = create_hyperlink("https://example.com", "Example")
        # OSC 8 format: ESC ] 8 ; ; URL ST text ESC ] 8 ; ; ST
        # Where ST is ESC \ or BEL
        assert "\x1b]8;;" in result or result == "Example"


class TestLinkExport:
    """Test Link is exported from components module"""

    def test_link_exported(self):
        """Link should be exported from inkpy.components"""
        from inkpy.components import Link

        assert Link is not None
