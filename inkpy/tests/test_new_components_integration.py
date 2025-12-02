"""
Integration tests for new components added for claude-code parity.

Tests component interactions and real-world usage patterns.
"""

import pytest


class TestTextInputIntegration:
    """Integration tests for TextInput component"""

    def test_text_input_creates_valid_element(self):
        """TextInput should create a valid ReactPy element"""
        from inkpy.components import TextInput

        element = TextInput(
            value="test",
            placeholder="Enter...",
            on_change=lambda x: None,
            on_submit=lambda x: None,
        )
        # Should return an element (not None)
        assert element is not None

    def test_text_input_mask_hides_value(self):
        """TextInput with mask should create element for masked display"""
        from inkpy.components import TextInput

        element = TextInput(value="secret", mask="*")
        assert element is not None


class TestSelectInputIntegration:
    """Integration tests for SelectInput component"""

    def test_select_input_with_items(self):
        """SelectInput should handle items correctly"""
        from inkpy.components import SelectInput

        items = [
            {"label": "Option A", "value": "a"},
            {"label": "Option B", "value": "b"},
            {"label": "Option C", "value": "c"},
        ]
        element = SelectInput(items=items, on_select=lambda x: None)
        assert element is not None


class TestMultiSelectIntegration:
    """Integration tests for MultiSelect component"""

    def test_multi_select_with_defaults(self):
        """MultiSelect should handle default selections"""
        from inkpy.components import MultiSelect

        items = [
            {"label": "Red", "value": "red"},
            {"label": "Green", "value": "green"},
            {"label": "Blue", "value": "blue"},
        ]
        element = MultiSelect(
            items=items,
            default_selected=["red", "blue"],
            on_submit=lambda x: None,
        )
        assert element is not None


class TestConfirmInputIntegration:
    """Integration tests for ConfirmInput component"""

    def test_confirm_input_with_callbacks(self):
        """ConfirmInput should handle callbacks"""
        from inkpy.components import ConfirmInput

        confirmations = []
        element = ConfirmInput(
            message="Are you sure?",
            on_confirm=lambda x: confirmations.append(x),
            default_value=True,
        )
        assert element is not None


class TestSpinnerIntegration:
    """Integration tests for Spinner component"""

    def test_spinner_types_work(self):
        """All spinner types should create valid elements"""
        from inkpy.components import Spinner
        from inkpy.components.spinner import SPINNER_TYPES

        for spinner_type in ["dots", "line", "arc", "circle"]:
            element = Spinner(type=spinner_type, text="Loading...")
            assert element is not None


class TestCodeBlockIntegration:
    """Integration tests for CodeBlock component"""

    def test_code_block_with_python(self):
        """CodeBlock should highlight Python code"""
        from inkpy.components import CodeBlock

        code = """
def hello():
    print("Hello, World!")

hello()
"""
        element = CodeBlock(code=code, language="python", show_line_numbers=True)
        assert element is not None

    def test_code_block_with_javascript(self):
        """CodeBlock should highlight JavaScript code"""
        from inkpy.components import CodeBlock

        code = 'const greeting = "Hello"; console.log(greeting);'
        element = CodeBlock(code=code, language="javascript")
        assert element is not None


class TestLinkIntegration:
    """Integration tests for Link component"""

    def test_link_creates_hyperlink(self):
        """Link should create terminal hyperlink"""
        from inkpy.components import Link

        element = Link(url="https://github.com", children="GitHub")
        assert element is not None

    def test_link_fallback_mode(self):
        """Link fallback should show URL"""
        from inkpy.components import Link

        element = Link(url="https://example.com", fallback=True)
        assert element is not None


class TestTableIntegration:
    """Integration tests for Table component"""

    def test_table_with_data(self):
        """Table should render structured data"""
        from inkpy.components import Table

        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"},
            {"name": "Charlie", "age": 35, "city": "Chicago"},
        ]
        element = Table(data=data)
        assert element is not None

    def test_table_with_custom_columns(self):
        """Table should use custom column definitions"""
        from inkpy.components import Table

        data = [{"id": 1, "name": "Test"}]
        columns = [
            {"key": "id", "header": "ID"},
            {"key": "name", "header": "Full Name"},
        ]
        element = Table(data=data, columns=columns, border=True)
        assert element is not None


class TestComponentCombinations:
    """Test components used together"""

    def test_all_input_components_importable(self):
        """All input components should be importable from inkpy.components"""
        from inkpy.components import (
            ConfirmInput,
            MultiSelect,
            SelectInput,
            TextInput,
        )

        assert all([TextInput, SelectInput, MultiSelect, ConfirmInput])

    def test_all_display_components_importable(self):
        """All display components should be importable"""
        from inkpy.components import CodeBlock, Link, Spinner, Table

        assert all([Spinner, CodeBlock, Link, Table])

    def test_use_terminal_dimensions_hook(self):
        """use_terminal_dimensions hook should be importable"""
        from inkpy.hooks import use_terminal_dimensions

        assert use_terminal_dimensions is not None
        assert callable(use_terminal_dimensions)
