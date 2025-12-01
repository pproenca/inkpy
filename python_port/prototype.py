import asyncio
from reactpy import component, html, use_effect, use_state
from reactpy.core.layout import Layout
from reactpy.core.hooks import create_context

# Mock Yoga Node for now
class YogaNode:
    def __init__(self, tag):
        self.tag = tag
        self.children = []
        self.props = {}

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"<{self.tag} props={self.props}>{self.children}</{self.tag}>"

@component
def Box(children, **kwargs):
    return html.div(children, **kwargs)

@component
def Text(children):
    return html.span(children)

@component
def App():
    count, set_count = use_state(0)

    @use_effect
    async def timer():
        while True:
            await asyncio.sleep(1)
            set_count(lambda c: c + 1)
            print(f"Tick: {count}")

    return Box(
        Text(f"Hello World! Count: {count}")
    )

async def run():
    # This is where we need to hook into ReactPy's layout engine
    # to receive updates and render them to our "Terminal DOM"
    
    app = App()
    layout = Layout(app)
    
    async with layout:
        while True:
            # Wait for an update
            await layout.render()
            
            # In a real implementation, we would traverse the layout.root
            # and build our Yoga tree, then calculate layout, then print.
            
            # For now, let's just inspect what we have.
            print("Rendered Update!")
            # Note: ReactPy's Layout doesn't expose a simple tree structure directly 
            # in the way we might expect for a TUI. We might need to implement a 
            # custom backend or traverse the internal state.
            
            # Let's try to see if we can get the VDOM state
            # layout.root is a Component instance, but we need the rendered nodes.
            
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run())
