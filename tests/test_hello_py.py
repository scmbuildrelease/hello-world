import pytest
from hello import hello_world

def test_hello_world_py():
    """
    Test the hello_world function in Python.
    """
    assert hello_world() == "Hello, World from Python!"
