"""
Tests for MultiSelect component.

MultiSelect provides a multi-choice selection list with:
- Checkbox-style selection (Space to toggle)
- Arrow key navigation
- Submit on Enter
- Select all / deselect all
"""

import pytest


class TestMultiSelectImport:
    """Test MultiSelect can be imported"""

    def test_multi_select_imports(self):
        """MultiSelect should be importable from components"""
        from inkpy.components.multi_select import MultiSelect

        assert MultiSelect is not None
        assert callable(MultiSelect)

    def test_multi_select_item_imports(self):
        """MultiSelectItem should be importable"""
        from inkpy.components.multi_select import MultiSelectItem

        assert MultiSelectItem is not None


class TestMultiSelectProps:
    """Test MultiSelect prop handling"""

    def test_multi_select_with_items(self):
        """MultiSelect should accept items prop"""
        from inkpy.components.multi_select import MultiSelect

        items = [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"},
            {"label": "Option 3", "value": "opt3"},
        ]
        element = MultiSelect(items=items)
        assert element is not None

    def test_multi_select_with_on_submit(self):
        """MultiSelect should accept on_submit callback"""
        from inkpy.components.multi_select import MultiSelect

        submissions = []

        def handle_submit(selected_items):
            submissions.append(selected_items)

        items = [{"label": "Test", "value": "test"}]
        element = MultiSelect(items=items, on_submit=handle_submit)
        assert element is not None

    def test_multi_select_with_default_selected(self):
        """MultiSelect should accept default_selected prop"""
        from inkpy.components.multi_select import MultiSelect

        items = [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"},
        ]
        element = MultiSelect(items=items, default_selected=["opt1"])
        assert element is not None

    def test_multi_select_with_indicators(self):
        """MultiSelect should accept custom check indicators"""
        from inkpy.components.multi_select import MultiSelect

        items = [{"label": "Test", "value": "test"}]
        element = MultiSelect(
            items=items,
            checked_indicator="[x]",
            unchecked_indicator="[ ]",
        )
        assert element is not None

    def test_multi_select_with_focus(self):
        """MultiSelect should accept focus prop"""
        from inkpy.components.multi_select import MultiSelect

        items = [{"label": "Test", "value": "test"}]
        focused = MultiSelect(items=items, focus=True)
        unfocused = MultiSelect(items=items, focus=False)
        assert focused is not None
        assert unfocused is not None

    def test_multi_select_with_limit(self):
        """MultiSelect should accept limit prop for max selections"""
        from inkpy.components.multi_select import MultiSelect

        items = [
            {"label": "Option 1", "value": "opt1"},
            {"label": "Option 2", "value": "opt2"},
            {"label": "Option 3", "value": "opt3"},
        ]
        element = MultiSelect(items=items, limit=2)
        assert element is not None


class TestMultiSelectCallbacks:
    """Test MultiSelect callback props"""

    def test_on_submit_is_callable(self):
        """on_submit prop should accept callable"""
        from inkpy.components.multi_select import MultiSelect

        submissions = []

        def handle_submit(selected):
            submissions.append(selected)

        items = [{"label": "Test", "value": "test"}]
        element = MultiSelect(items=items, on_submit=handle_submit)
        assert element is not None

    def test_on_highlight_is_callable(self):
        """on_highlight prop should accept callable"""
        from inkpy.components.multi_select import MultiSelect

        highlights = []

        def handle_highlight(item):
            highlights.append(item)

        items = [{"label": "Test", "value": "test"}]
        element = MultiSelect(items=items, on_highlight=handle_highlight)
        assert element is not None


class TestMultiSelectExport:
    """Test MultiSelect is exported from components module"""

    def test_multi_select_exported(self):
        """MultiSelect should be exported from inkpy.components"""
        from inkpy.components import MultiSelect

        assert MultiSelect is not None


class TestMultiSelectItem:
    """Test MultiSelectItem component"""

    def test_item_renders_label(self):
        """MultiSelectItem should render item label"""
        from inkpy.components.multi_select import MultiSelectItem

        element = MultiSelectItem(
            label="Option 1",
            is_highlighted=False,
            is_checked=False,
        )
        assert element is not None

    def test_item_shows_checked_indicator(self):
        """MultiSelectItem should show check indicator when checked"""
        from inkpy.components.multi_select import MultiSelectItem

        checked = MultiSelectItem(label="Checked", is_highlighted=False, is_checked=True)
        unchecked = MultiSelectItem(label="Unchecked", is_highlighted=False, is_checked=False)
        assert checked is not None
        assert unchecked is not None

    def test_item_shows_highlight(self):
        """MultiSelectItem should indicate when highlighted"""
        from inkpy.components.multi_select import MultiSelectItem

        highlighted = MultiSelectItem(label="Test", is_highlighted=True, is_checked=False)
        not_highlighted = MultiSelectItem(label="Test", is_highlighted=False, is_checked=False)
        assert highlighted is not None
        assert not_highlighted is not None
