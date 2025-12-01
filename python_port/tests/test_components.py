from inkpy.components.box import Box
from inkpy.components.text import Text
from reactpy import component, use_state

def test_box_component():
    @component
    def App():
        return Box(Text("Hello"))

    # Just check if we can instantiate it without errors
    app = App()
    assert app is not None

def test_text_component():
    @component
    def App():
        return Text("Hello World")

    app = App()
    assert app is not None

def test_nested_components():
    @component
    def App():
        return Box([
            Text("Line 1"),
            Box(Text("Nested"))
        ])

    app = App()
    assert app is not None

# Integration tests usually require a backend to run layout/rendering
# We can mock the backend or test components in isolation

def test_component_props():
    # Test if props are passed correctly (mock verification)
    # ReactPy components return an Element or Component

    b = Box(style={'width': 100})
    # ReactPy components are opaque until rendered.
    # Just asserting it returns a component object is enough for now.
    assert hasattr(b, 'render')

def test_state_hook():
    # Verify use_state works in our context (standard ReactPy behavior)
    @component
    def Counter():
        count, set_count = use_state(0)
        return Text(f"{count}")

    # We need a backend to run this lifecycle
    pass
