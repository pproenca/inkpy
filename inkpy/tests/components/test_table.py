"""
Tests for Table component.

Table provides structured data display with:
- Column headers
- Row data
- Border styles
- Alignment options
"""

import pytest


class TestTableImport:
    """Test Table component can be imported"""

    def test_table_imports(self):
        """Table should be importable from components"""
        from inkpy.components.table import Table

        assert Table is not None
        assert callable(Table)


class TestTableProps:
    """Test Table prop handling"""

    def test_table_with_data(self):
        """Table should accept data prop"""
        from inkpy.components.table import Table

        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        element = Table(data=data)
        assert element is not None

    def test_table_with_columns(self):
        """Table should accept columns prop for header customization"""
        from inkpy.components.table import Table

        data = [{"name": "Alice", "age": 30}]
        columns = [
            {"key": "name", "header": "Name"},
            {"key": "age", "header": "Age"},
        ]
        element = Table(data=data, columns=columns)
        assert element is not None

    def test_table_with_border(self):
        """Table should accept border prop"""
        from inkpy.components.table import Table

        data = [{"col": "value"}]
        with_border = Table(data=data, border=True)
        without_border = Table(data=data, border=False)
        assert with_border is not None
        assert without_border is not None

    def test_table_with_header(self):
        """Table should accept show_header prop"""
        from inkpy.components.table import Table

        data = [{"col": "value"}]
        with_header = Table(data=data, show_header=True)
        without_header = Table(data=data, show_header=False)
        assert with_header is not None
        assert without_header is not None

    def test_table_with_padding(self):
        """Table should accept cell_padding prop"""
        from inkpy.components.table import Table

        data = [{"col": "value"}]
        element = Table(data=data, cell_padding=2)
        assert element is not None


class TestTableCell:
    """Test TableCell component"""

    def test_table_cell_imports(self):
        """TableCell should be importable"""
        from inkpy.components.table import TableCell

        assert TableCell is not None

    def test_table_cell_renders(self):
        """TableCell should render content"""
        from inkpy.components.table import TableCell

        element = TableCell(content="Hello", width=10)
        assert element is not None


class TestTableRow:
    """Test TableRow component"""

    def test_table_row_imports(self):
        """TableRow should be importable"""
        from inkpy.components.table import TableRow

        assert TableRow is not None

    def test_table_row_renders(self):
        """TableRow should render cells"""
        from inkpy.components.table import TableRow

        cells = ["A", "B", "C"]
        widths = [5, 5, 5]
        element = TableRow(cells=cells, widths=widths)
        assert element is not None


class TestTableExport:
    """Test Table is exported from components module"""

    def test_table_exported(self):
        """Table should be exported from inkpy.components"""
        from inkpy.components import Table

        assert Table is not None
