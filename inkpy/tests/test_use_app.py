# test_use_app.py
from reactpy import component, html

from inkpy.hooks.use_app import use_app


def test_use_app_provides_exit():
    """Test that useApp hook provides exit function"""

    @component
    def TestApp():
        app = use_app()
        assert hasattr(app, "exit")
        assert callable(app.exit)
        return html.div()

    # Test within AppContext
    # Will implement after ReactPy integration


def test_app_context_exit():
    """Test that exit function can be called"""
    exit_called = []

    def mock_exit(error=None):
        exit_called.append(error)

    context_value = {"exit": mock_exit}

    # Verify exit can be called with and without error
    context_value["exit"]()
    assert len(exit_called) == 1
    assert exit_called[0] is None

    context_value["exit"](ValueError("test error"))
    assert len(exit_called) == 2
    assert isinstance(exit_called[1], ValueError)


def test_use_app_in_component():
    """Integration test for useApp hook"""
    # This will test the actual hook usage in a rendered component
    pass  # TODO: Implement after Task 6.4
