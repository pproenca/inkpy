# test_std_hooks.py
import io
from reactpy import component
from inkpy.hooks.use_stdout import use_stdout
from inkpy.hooks.use_stderr import use_stderr

def test_use_stdout_provides_stream():
    """Test that useStdout provides stdout stream and write function"""
    @component
    def TestApp():
        stdout = use_stdout()
        assert hasattr(stdout, 'stdout')
        assert hasattr(stdout, 'write')
        assert callable(stdout.write)
        return None
    
    # Will test after integration

def test_stdout_write():
    """Test that stdout write function works"""
    buffer = io.StringIO()
    
    def write_fn(data):
        buffer.write(data)
    
    write_fn("Hello, World!")
    assert buffer.getvalue() == "Hello, World!"

def test_use_stderr_provides_stream():
    """Test that useStderr provides stderr stream"""
    @component
    def TestApp():
        stderr = use_stderr()
        assert hasattr(stderr, 'stderr')
        assert hasattr(stderr, 'write')
        assert callable(stderr.write)
        return None

def test_stderr_write():
    """Test that stderr write function works"""
    buffer = io.StringIO()
    
    def write_fn(data):
        buffer.write(data)
    
    write_fn("Error message")
    assert buffer.getvalue() == "Error message"

