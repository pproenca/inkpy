from inkpy.input.keypress import parse_keypress


def test_parse_arrow_keys():
    """Test parsing arrow keys"""
    key = parse_keypress("\x1b[A")  # Up arrow
    assert key.name == "up"
    assert key.upArrow is True

    key = parse_keypress("\x1b[B")  # Down arrow
    assert key.name == "down"
    assert key.downArrow is True

    key = parse_keypress("\x1b[C")  # Right arrow
    assert key.name == "right"
    assert key.rightArrow is True

    key = parse_keypress("\x1b[D")  # Left arrow
    assert key.name == "left"
    assert key.leftArrow is True


def test_parse_ctrl_c():
    """Test parsing Ctrl+C"""
    key = parse_keypress("\x03")
    assert key.name == "c"
    assert key.ctrl is True


def test_parse_enter():
    """Test parsing Enter key"""
    key = parse_keypress("\r")
    assert key.name == "return"
    assert key.return_ is True


def test_parse_escape():
    """Test parsing Escape key"""
    key = parse_keypress("\x1b")
    assert key.name == "escape"
    assert key.escape is True


def test_parse_tab():
    """Test parsing Tab key"""
    key = parse_keypress("\t")
    assert key.name == "tab"
    assert key.tab is True


def test_parse_backspace():
    """Test parsing Backspace key"""
    key = parse_keypress("\b")
    assert key.name == "backspace"
    assert key.backspace is True


def test_parse_delete():
    """Test parsing Delete key"""
    key = parse_keypress("\x7f")
    assert key.name == "delete"
    assert key.delete is True


def test_parse_page_up_down():
    """Test parsing Page Up/Down"""
    key = parse_keypress("\x1b[5~")  # Page Up
    assert key.name == "pageup"
    assert key.pageUp is True

    key = parse_keypress("\x1b[6~")  # Page Down
    assert key.name == "pagedown"
    assert key.pageDown is True


def test_parse_function_keys():
    """Test parsing function keys"""
    key = parse_keypress("\x1bOP")  # F1
    assert key.name == "f1"

    key = parse_keypress("\x1bOQ")  # F2
    assert key.name == "f2"


def test_parse_regular_characters():
    """Test parsing regular characters"""
    key = parse_keypress("a")
    assert key.name == "a"
    assert key.ctrl is False
    assert key.shift is False


def test_parse_shift_characters():
    """Test parsing shift+character"""
    key = parse_keypress("A")
    assert key.name == "a"
    assert key.shift is True


def test_parse_ctrl_combinations():
    """Test parsing Ctrl+key combinations"""
    key = parse_keypress("\x01")  # Ctrl+A
    assert key.name == "a"
    assert key.ctrl is True


# === Snake_case alias tests ===


def test_key_snake_case_arrow_properties():
    """Test Key class has both camelCase and snake_case properties for arrows"""
    key = parse_keypress("\x1b[A")  # Up arrow

    # CamelCase (existing)
    assert key.upArrow is True

    # Snake_case (NEW)
    assert key.up_arrow is True
    assert key.down_arrow is False


def test_key_snake_case_all_arrows():
    """Test all arrow snake_case aliases"""
    # Up arrow
    key = parse_keypress("\x1b[A")
    assert key.up_arrow is True
    assert key.down_arrow is False
    assert key.left_arrow is False
    assert key.right_arrow is False

    # Down arrow
    key = parse_keypress("\x1b[B")
    assert key.down_arrow is True

    # Left arrow
    key = parse_keypress("\x1b[D")
    assert key.left_arrow is True

    # Right arrow
    key = parse_keypress("\x1b[C")
    assert key.right_arrow is True


def test_key_return_alias():
    """Test return key has both return_ and return_key aliases"""
    key = parse_keypress("\r")
    assert key.return_ is True
    assert key.return_key is True  # Alias for convenience


def test_key_page_snake_case_aliases():
    """Test page_up and page_down snake_case aliases"""
    key = parse_keypress("\x1b[5~")  # Page Up
    assert key.pageUp is True
    assert key.page_up is True

    key = parse_keypress("\x1b[6~")  # Page Down
    assert key.pageDown is True
    assert key.page_down is True


def test_key_all_snake_case_aliases_exist():
    """Test all snake_case aliases exist as attributes"""
    key = parse_keypress("a")

    # All arrow properties should exist in snake_case
    assert hasattr(key, "up_arrow")
    assert hasattr(key, "down_arrow")
    assert hasattr(key, "left_arrow")
    assert hasattr(key, "right_arrow")
    assert hasattr(key, "page_up")
    assert hasattr(key, "page_down")
    assert hasattr(key, "return_key")
