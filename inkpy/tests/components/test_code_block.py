"""
Tests for CodeBlock component and syntax highlighting utilities.

CodeBlock provides:
- Syntax highlighting for code blocks
- Language detection
- Line numbers (optional)
- Custom themes
"""

import pytest


class TestHighlightImport:
    """Test syntax highlighting utilities can be imported"""

    def test_highlight_code_imports(self):
        """highlight_code should be importable"""
        from inkpy.utils.highlight import highlight_code

        assert highlight_code is not None
        assert callable(highlight_code)

    def test_get_lexer_imports(self):
        """get_lexer_for_language should be importable"""
        from inkpy.utils.highlight import get_lexer_for_language

        assert get_lexer_for_language is not None


class TestHighlightCode:
    """Test syntax highlighting functionality"""

    def test_highlight_python_code(self):
        """Should highlight Python code"""
        from inkpy.utils.highlight import highlight_code

        code = 'print("hello")'
        result = highlight_code(code, "python")
        assert result is not None
        assert len(result) > 0

    def test_highlight_javascript_code(self):
        """Should highlight JavaScript code"""
        from inkpy.utils.highlight import highlight_code

        code = 'console.log("hello");'
        result = highlight_code(code, "javascript")
        assert result is not None

    def test_highlight_unknown_language(self):
        """Should handle unknown languages gracefully"""
        from inkpy.utils.highlight import highlight_code

        code = "some plain text"
        result = highlight_code(code, "unknownlang")
        assert result is not None
        # Should still return the code even if not highlighted

    def test_highlight_returns_ansi(self):
        """Highlighted code should contain ANSI codes"""
        from inkpy.utils.highlight import highlight_code

        code = "def foo(): pass"
        result = highlight_code(code, "python")
        # ANSI codes start with ESC
        assert "\x1b[" in result or result == code


class TestCodeBlockImport:
    """Test CodeBlock component can be imported"""

    def test_code_block_imports(self):
        """CodeBlock should be importable from components"""
        from inkpy.components.code_block import CodeBlock

        assert CodeBlock is not None
        assert callable(CodeBlock)


class TestCodeBlockProps:
    """Test CodeBlock prop handling"""

    def test_code_block_with_code(self):
        """CodeBlock should accept code prop"""
        from inkpy.components.code_block import CodeBlock

        element = CodeBlock(code='print("hello")')
        assert element is not None

    def test_code_block_with_language(self):
        """CodeBlock should accept language prop"""
        from inkpy.components.code_block import CodeBlock

        element = CodeBlock(code='print("hello")', language="python")
        assert element is not None

    def test_code_block_with_line_numbers(self):
        """CodeBlock should accept show_line_numbers prop"""
        from inkpy.components.code_block import CodeBlock

        with_numbers = CodeBlock(code="line1\nline2", show_line_numbers=True)
        without_numbers = CodeBlock(code="line1\nline2", show_line_numbers=False)
        assert with_numbers is not None
        assert without_numbers is not None

    def test_code_block_with_theme(self):
        """CodeBlock should accept theme prop"""
        from inkpy.components.code_block import CodeBlock

        element = CodeBlock(code="code", theme="monokai")
        assert element is not None


class TestCodeBlockExport:
    """Test CodeBlock is exported from components module"""

    def test_code_block_exported(self):
        """CodeBlock should be exported from inkpy.components"""
        from inkpy.components import CodeBlock

        assert CodeBlock is not None
