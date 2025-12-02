"""
Table component module.

Provides structured data display in a terminal-friendly table format.
"""

from typing import Any, Optional

from reactpy import component, html


@component
def TableCell(
    content: str = "",
    width: int = 10,
    align: str = "left",
    padding: int = 1,
):
    """
    A single cell in a table.

    Args:
        content: Cell content text
        width: Cell width in characters
        align: Text alignment ('left', 'center', 'right')
        padding: Horizontal padding
    """
    # Truncate or pad content to fit width
    effective_width = max(1, width - padding * 2)
    text = str(content)[:effective_width]

    if align == "center":
        text = text.center(effective_width)
    elif align == "right":
        text = text.rjust(effective_width)
    else:
        text = text.ljust(effective_width)

    # Add padding
    padded = " " * padding + text + " " * padding

    return html.span({}, padded)


@component
def TableRow(
    cells: list[str],
    widths: list[int],
    is_header: bool = False,
    separator: str = "|",
    padding: int = 1,
    header_style: Optional[dict[str, Any]] = None,
):
    """
    A row in a table.

    Args:
        cells: List of cell contents
        widths: List of column widths
        is_header: Whether this is a header row
        separator: Column separator character
        padding: Cell padding
        header_style: Style dict for header cells (overrides defaults)
    """
    children = []

    for i, (cell, width) in enumerate(zip(cells, widths)):
        if i > 0:
            children.append(html.span({"style": {"color": "gray"}}, separator))

        style = {}
        if is_header:
            # Default header style
            style["fontWeight"] = "bold"
            # Apply custom header_style if provided
            if header_style:
                style.update(header_style)

        children.append(
            html.span(
                {"style": style},
                TableCell(content=str(cell), width=width, padding=padding),
            )
        )

    return html.div({"style": {"flexDirection": "row"}}, *children)


@component
def Table(
    data: Optional[list[dict[str, Any]]] = None,
    columns: Optional[list[dict[str, str]]] = None,
    border: bool = False,
    show_header: bool = True,
    cell_padding: int = 1,
    min_column_width: int = 5,
    header_style: Optional[dict[str, Any]] = None,
):
    """
    Table component for displaying structured data.

    Args:
        data: List of row dictionaries
        columns: Column definitions with 'key' and 'header'
        border: Whether to show table border
        show_header: Whether to show column headers
        cell_padding: Horizontal padding in cells
        min_column_width: Minimum column width
        header_style: Style dict for header row (e.g., {"bold": True, "color": "cyan"})

    Example:
        @component
        def App():
            data = [
                {"name": "Alice", "age": 30, "city": "NYC"},
                {"name": "Bob", "age": 25, "city": "LA"},
            ]
            columns = [
                {"key": "name", "header": "Name"},
                {"key": "age", "header": "Age"},
                {"key": "city", "header": "City"},
            ]
            return Table(
                data=data,
                columns=columns,
                border=True,
                header_style={"color": "cyan"}
            )
    """
    if data is None:
        data = []

    if not data:
        return html.div({}, "(empty table)")

    # Auto-detect columns if not provided
    if columns is None:
        # Get all keys from first row
        first_row = data[0]
        columns = [{"key": k, "header": k.title()} for k in first_row]

    # Calculate column widths
    widths = []
    for col in columns:
        key = col["key"]
        header = col.get("header", key)

        # Find max width needed for this column
        max_width = len(str(header))
        for row in data:
            value = row.get(key, "")
            max_width = max(max_width, len(str(value)))

        # Add padding and enforce minimum
        width = max(min_column_width, max_width + cell_padding * 2)
        widths.append(width)

    # Build table rows
    children = []

    # Header row
    if show_header:
        headers = [col.get("header", col["key"]) for col in columns]
        children.append(
            TableRow(
                cells=headers,
                widths=widths,
                is_header=True,
                padding=cell_padding,
                header_style=header_style,
            )
        )

        # Header separator
        separator_line = "─" * (sum(widths) + len(widths) - 1)
        children.append(html.div({"style": {"color": "gray"}}, separator_line))

    # Data rows
    for row in data:
        cells = [str(row.get(col["key"], "")) for col in columns]
        children.append(
            TableRow(
                cells=cells,
                widths=widths,
                is_header=False,
                padding=cell_padding,
            )
        )

    # Wrap in border if requested
    style = {"flexDirection": "column"}
    if border:
        style["borderStyle"] = "single"
        style["paddingLeft"] = 1
        style["paddingRight"] = 1

    return html.div({"style": style}, *children)
