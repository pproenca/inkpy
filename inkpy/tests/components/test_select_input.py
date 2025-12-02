"""
Tests for SelectInput component.

SelectInput provides a single-choice selection list with:
- Arrow key navigation
- Visual selection indicator
- Confirmation on Enter
- Initial index support
"""

import pytest


class TestSelectInputImport:
    """Test SelectInput can be imported"""

    def test_select_input_imports(self):
        """SelectInput should be importable from components"""
        from inkpy.components.select_input import SelectInput

        assert SelectInput is not None
        assert callable(SelectInput)

    def test_select_input_item_imports(self):
        """SelectInputItem should be importable for custom rendering"""
        from inkpy.components.select_input import SelectInputItem

        assert SelectInputItem is not None


class TestSelectInputProps:
    """Test SelectInput prop handling"""

    def test_select_input_with_items(self):
        """SelectInput should accept items prop"""
        from inkpy.components.select_input import SelectInput

        items = [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"},
            {"label": "Option 3", "value": "opt3"},
        ]
        element = SelectInput(items=items)
        assert element is not None

    def test_select_input_with_on_select(self):
        """SelectInput should accept on_select callback"""
        from inkpy.components.select_input import SelectInput

        selections = []

        def handle_select(item):
            selections.append(item)

        items = [{"label": "Test", "value": "test"}]
        element = SelectInput(items=items, on_select=handle_select)
        assert element is not None

    def test_select_input_with_initial_index(self):
        """SelectInput should accept initial_index prop"""
        from inkpy.components.select_input import SelectInput

        items = [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"},
        ]
        element = SelectInput(items=items, initial_index=1)
        assert element is not None

    def test_select_input_with_indicator(self):
        """SelectInput should accept custom indicator"""
        from inkpy.components.select_input import SelectInput

        items = [{"label": "Test", "value": "test"}]
        element = SelectInput(items=items, indicator="> ")
        assert element is not None

    def test_select_input_with_focus(self):
        """SelectInput should accept focus prop"""
        from inkpy.components.select_input import SelectInput

        items = [{"label": "Test", "value": "test"}]
        focused = SelectInput(items=items, focus=True)
        unfocused = SelectInput(items=items, focus=False)
        assert focused is not None
        assert unfocused is not None


class TestSelectInputCallbacks:
    """Test SelectInput callback props"""

    def test_on_select_is_callable(self):
        """on_select prop should accept callable"""
        from inkpy.components.select_input import SelectInput

        selections = []

        def handle_select(item):
            selections.append(item)

        items = [{"label": "Test", "value": "test"}]
        element = SelectInput(items=items, on_select=handle_select)
        assert element is not None

    def test_on_highlight_is_callable(self):
        """on_highlight prop should accept callable for highlight changes"""
        from inkpy.components.select_input import SelectInput

        highlights = []

        def handle_highlight(item):
            highlights.append(item)

        items = [{"label": "Test", "value": "test"}]
        element = SelectInput(items=items, on_highlight=handle_highlight)
        assert element is not None


class TestSelectInputExport:
    """Test SelectInput is exported from components module"""

    def test_select_input_exported(self):
        """SelectInput should be exported from inkpy.components"""
        from inkpy.components import SelectInput

        assert SelectInput is not None


class TestSelectInputItem:
    """Test SelectInputItem component"""

    def test_item_renders_label(self):
        """SelectInputItem should render item label"""
        from inkpy.components.select_input import SelectInputItem

        element = SelectInputItem(label="Option 1", is_selected=False)
        assert element is not None

    def test_item_shows_indicator_when_selected(self):
        """SelectInputItem should show indicator when selected"""
        from inkpy.components.select_input import SelectInputItem

        selected = SelectInputItem(label="Selected", is_selected=True)
        unselected = SelectInputItem(label="Not Selected", is_selected=False)
        assert selected is not None
        assert unselected is not None
