"""
ErrorOverview component - Displays error information with stack trace and code excerpt
"""
import os
import traceback
import linecache
from typing import Optional, List, Tuple
from reactpy import component
from inkpy.components.box import Box
from inkpy.components.text import Text


def _cleanup_path(path: Optional[str]) -> Optional[str]:
    """
    Clean up file path by removing file:// prefix and current working directory.
    
    Args:
        path: File path to clean
        
    Returns:
        Cleaned path or None
    """
    if not path:
        return None
    
    cwd = os.getcwd()
    # Remove file:// prefix if present
    if path.startswith('file://'):
        path = path[7:]
    
    # Remove cwd prefix if present
    if path.startswith(cwd + '/'):
        path = path[len(cwd) + 1:]
    
    return path


def _parse_stack_line(line: str) -> Optional[dict]:
    """
    Parse a stack trace line to extract file, line, column, and function.
    
    Args:
        line: Stack trace line (e.g., "  File \"/path/to/file.py\", line 10, in function_name")
        
    Returns:
        Dictionary with 'file', 'line', 'column', 'function' or None
    """
    if not line.strip():
        return None
    
    # Try to parse Python stack trace format
    # Format: "  File \"/path/to/file.py\", line 10, in function_name"
    import re
    
    # Match: File "path", line N, in function
    match = re.match(r'\s*File\s+"([^"]+)",\s*line\s+(\d+)(?:,\s*in\s+(.+))?', line)
    if match:
        file_path, line_num, function = match.groups()
        return {
            'file': file_path,
            'line': int(line_num),
            'column': 0,  # Python doesn't provide column in standard traceback
            'function': function or '<module>'
        }
    
    return None


def _get_code_excerpt(file_path: str, line_num: int, context_lines: int = 3) -> Optional[List[Tuple[int, str]]]:
    """
    Get code excerpt around a specific line number.
    
    Args:
        file_path: Path to source file
        line_num: Line number to center excerpt on
        context_lines: Number of lines before and after
        
    Returns:
        List of tuples (line_number, line_content) or None
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        excerpt = []
        start_line = max(1, line_num - context_lines)
        end_line = line_num + context_lines
        
        for i in range(start_line, end_line + 1):
            line_content = linecache.getline(file_path, i)
            if line_content:
                excerpt.append((i, line_content.rstrip('\n\r')))
        
        return excerpt if excerpt else None
    except Exception:
        return None


@component
def ErrorOverview(error: Exception):
    """
    ErrorOverview component - Displays error with stack trace and code excerpt.
    
    Args:
        error: Exception to display
    """
    # Get stack trace
    stack_lines = []
    if error.__traceback__:
        tb_lines = traceback.format_tb(error.__traceback__)
        stack_lines = [line.strip() for line in tb_lines]
    
    # Parse origin (first stack frame)
    origin = None
    file_path = None
    if stack_lines:
        origin = _parse_stack_line(stack_lines[0])
        if origin:
            file_path = _cleanup_path(origin.get('file'))
    
    # Get code excerpt if file is available
    excerpt = None
    line_width = 0
    if file_path and origin and origin.get('line'):
        excerpt = _get_code_excerpt(file_path, origin['line'])
        if excerpt:
            line_width = max(len(str(line_num)) for line_num, _ in excerpt)
    
    # Build children components
    children = []
    
    # Error header with ERROR label
    error_header = Box(children=[
        Text(" ERROR ", backgroundColor="red", color="white"),
        Text(f" {str(error)}")
    ])
    children.append(error_header)
    
    # File location
    if origin and file_path:
        location_text = f"{file_path}:{origin.get('line', '?')}:{origin.get('column', '?')}"
        children.append(Box(
            style={'marginTop': 1},
            children=[
                Text(location_text, dimColor=True)
            ]
        ))
    
    # Code excerpt
    if origin and excerpt:
        excerpt_children = []
        for line_num, line_content in excerpt:
            is_error_line = line_num == origin.get('line')
            
            # Line number with padding
            line_num_text = str(line_num).rjust(line_width) + ":"
            line_num_component = Box(
                style={'width': line_width + 1},
                children=[
                    Text(
                        line_num_text,
                        dimColor=not is_error_line,
                        backgroundColor="red" if is_error_line else None,
                        color="white" if is_error_line else None,
                        aria_label=f"Line {line_num}{', error' if is_error_line else ''}"
                    )
                ]
            )
            
            # Line content
            line_content_component = Text(
                f" {line_content}",
                backgroundColor="red" if is_error_line else None,
                color="white" if is_error_line else None
            )
            
            excerpt_children.append(Box(children=[
                line_num_component,
                line_content_component
            ]))
        
        children.append(Box(
            style={'marginTop': 1, 'flexDirection': 'column'},
            children=excerpt_children
        ))
    
    # Stack trace
    if stack_lines:
        stack_children = []
        for line in stack_lines[1:]:  # Skip first line (already shown in excerpt)
            parsed_line = _parse_stack_line(line)
            
            if not parsed_line:
                # Unparseable line - show as-is
                stack_children.append(Box(children=[
                    Text("- ", dimColor=True),
                    Text(line + "\t ", dimColor=True, bold=True)
                ]))
            else:
                # Parseable line - show function and location
                parsed_file = _cleanup_path(parsed_line.get('file'))
                file_location = f"{parsed_file or ''}:{parsed_line.get('line', '?')}:{parsed_line.get('column', '?')}"
                
                stack_children.append(Box(children=[
                    Text("- ", dimColor=True),
                    Text(parsed_line.get('function', '<unknown>'), dimColor=True, bold=True),
                    Text(
                        f" ({file_location})",
                        dimColor=True,
                        color="gray",
                        aria_label=f"at {parsed_file or ''} line {parsed_line.get('line', '?')} column {parsed_line.get('column', '?')}"
                    )
                ]))
        
        if stack_children:
            children.append(Box(
                style={'marginTop': 1, 'flexDirection': 'column'},
                children=stack_children
            ))
    
    return Box(
        style={'flexDirection': 'column', 'padding': 1},
        children=children
    )

