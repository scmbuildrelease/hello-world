# Hello World Project

This is a simple project demonstrating Hello World implementations in Python and C.

## Project Structure
- `hello.py`: Python Hello World implementation
- `hello.c`: C Hello World implementation

## Setup and Installation
```bash
# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install the package
pip install .

# Run Python hello world
python hello.py

# Compile and run C program
gcc hello.c -o hello_c
./hello_c
