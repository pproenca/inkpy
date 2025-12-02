"""
Tests for ConfirmInput component.

ConfirmInput provides a Yes/No confirmation dialog with:
- Y/N keyboard shortcuts
- Default value support
- Customizable labels
"""

import pytest


class TestConfirmInputImport:
    """Test ConfirmInput can be imported"""

    def test_confirm_input_imports(self):
        """ConfirmInput should be importable from components"""
        from inkpy.components.confirm_input import ConfirmInput

        assert ConfirmInput is not None
        assert callable(ConfirmInput)


class TestConfirmInputProps:
    """Test ConfirmInput prop handling"""

    def test_confirm_input_with_message(self):
        """ConfirmInput should accept message prop"""
        from inkpy.components.confirm_input import ConfirmInput

        element = ConfirmInput(message="Are you sure?")
        assert element is not None

    def test_confirm_input_with_on_confirm(self):
        """ConfirmInput should accept on_confirm callback"""
        from inkpy.components.confirm_input import ConfirmInput

        confirmations = []

        def handle_confirm(value):
            confirmations.append(value)

        element = ConfirmInput(message="Confirm?", on_confirm=handle_confirm)
        assert element is not None

    def test_confirm_input_with_default_value(self):
        """ConfirmInput should accept default_value prop"""
        from inkpy.components.confirm_input import ConfirmInput

        default_true = ConfirmInput(message="Yes default?", default_value=True)
        default_false = ConfirmInput(message="No default?", default_value=False)
        assert default_true is not None
        assert default_false is not None

    def test_confirm_input_with_custom_labels(self):
        """ConfirmInput should accept custom yes/no labels"""
        from inkpy.components.confirm_input import ConfirmInput

        element = ConfirmInput(
            message="Continue?",
            yes_label="Yes",
            no_label="No",
        )
        assert element is not None

    def test_confirm_input_with_focus(self):
        """ConfirmInput should accept focus prop"""
        from inkpy.components.confirm_input import ConfirmInput

        focused = ConfirmInput(message="Confirm?", focus=True)
        unfocused = ConfirmInput(message="Confirm?", focus=False)
        assert focused is not None
        assert unfocused is not None


class TestConfirmInputCallbacks:
    """Test ConfirmInput callback props"""

    def test_on_confirm_is_callable(self):
        """on_confirm prop should accept callable"""
        from inkpy.components.confirm_input import ConfirmInput

        confirmations = []

        def handle_confirm(value):
            confirmations.append(value)

        element = ConfirmInput(message="Confirm?", on_confirm=handle_confirm)
        assert element is not None


class TestConfirmInputExport:
    """Test ConfirmInput is exported from components module"""

    def test_confirm_input_exported(self):
        """ConfirmInput should be exported from inkpy.components"""
        from inkpy.components import ConfirmInput

        assert ConfirmInput is not None
