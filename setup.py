from setuptools import setup, Extension

# C extension module
hello_module = Extension(
    'hello_c', 
    sources=['hello.c'],
    extra_compile_args=['-Wall']
)

setup(
    name='hello-world',
    version='0.1.0',
    description='A simple Hello World project with Python and C',
    ext_modules=[hello_module],
    packages=['hello_world'],
    author='Your Name',
    author_email='your.email@example.com'
)
