"""
Tests for TextInput component.

TextInput provides a controlled text input field with:
- Value and onChange handling
- Cursor management
- Submit on Enter
- Placeholder support
- Password masking
"""

import pytest


class TestTextInputImport:
    """Test TextInput can be imported"""

    def test_text_input_imports(self):
        """TextInput should be importable from components"""
        from inkpy.components.text_input import TextInput

        assert TextInput is not None
        assert callable(TextInput)


class TestTextInputCallbacks:
    """Test TextInput callback props"""

    def test_on_change_is_callable(self):
        """on_change prop should accept callable"""
        from inkpy.components.text_input import TextInput

        changes = []

        def handle_change(value):
            changes.append(value)

        # TextInput accepts callbacks
        element = TextInput(value="", on_change=handle_change)
        assert element is not None

    def test_on_submit_is_callable(self):
        """on_submit prop should accept callable"""
        from inkpy.components.text_input import TextInput

        submits = []

        def handle_submit(value):
            submits.append(value)

        element = TextInput(value="test", on_submit=handle_submit)
        assert element is not None


class TestTextInputProps:
    """Test TextInput prop handling"""

    def test_text_input_with_value(self):
        """TextInput should accept value prop"""
        from inkpy.components.text_input import TextInput

        element = TextInput(value="hello world")
        assert element is not None

    def test_text_input_with_placeholder(self):
        """TextInput should accept placeholder prop"""
        from inkpy.components.text_input import TextInput

        element = TextInput(value="", placeholder="Enter text...")
        assert element is not None

    def test_text_input_with_mask(self):
        """TextInput should accept mask prop for password mode"""
        from inkpy.components.text_input import TextInput

        element = TextInput(value="secret", mask="*")
        assert element is not None

    def test_text_input_with_focus(self):
        """TextInput should accept focus prop"""
        from inkpy.components.text_input import TextInput

        focused = TextInput(value="test", focus=True)
        unfocused = TextInput(value="test", focus=False)
        assert focused is not None
        assert unfocused is not None

    def test_text_input_all_props(self):
        """TextInput should accept all documented props"""
        from inkpy.components.text_input import TextInput

        element = TextInput(
            value="test",
            placeholder="Enter text",
            on_change=lambda x: None,
            on_submit=lambda x: None,
            focus=True,
            mask=None,
            show_cursor=True,
        )
        assert element is not None


class TestTextInputExport:
    """Test TextInput is exported from components module"""

    def test_text_input_exported(self):
        """TextInput should be exported from inkpy.components"""
        # This will fail until we add it to __init__.py
        from inkpy.components import TextInput

        assert TextInput is not None
