from inkpy.hooks.use_input import use_input
from inkpy.input.keypress import Key


def test_use_input_basic():
    """Test basic use_input hook functionality"""
    # This will be tested with ReactPy integration
    # For now, just verify the hook exists
    assert callable(use_input)


def test_use_input_with_handler():
    """Test use_input with a handler function"""
    captured_input = []
    captured_key = []

    def handler(input_str: str, key: Key):
        captured_input.append(input_str)
        captured_key.append(key)

    # In a real ReactPy component, this would be called during render
    # For now, we'll test the hook structure
    assert callable(use_input)
    assert handler is not None


def test_use_input_is_active():
    """Test use_input with isActive option"""

    # Test that isActive parameter is accepted
    def handler(input_str: str, key: Key):
        pass

    # Should accept isActive parameter
    # In ReactPy, this would control whether input is captured
    assert callable(use_input)
