import pytest
import ctypes
import os

def test_hello_world_c():
    """
    Test the hello world function from the C module.
    """
    # Build the shared library
    import subprocess
    subprocess.run(['gcc', '-shared', '-o', 'libhello.so', 'hello.c'], check=True)
    
    # Load the library
    lib = ctypes.CDLL('./libhello.so')
    
    # Set return type
    lib.hello_world_c.restype = ctypes.c_char_p
    
    # Call the function and decode
    result = lib.hello_world_c().decode('utf-8')
    
    assert result == "Hello, World from C!"
