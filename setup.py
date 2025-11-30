"""
Minimal setup.py for C extension only
All metadata is in pyproject.toml
"""
import sys
from setuptools import setup, Extension

# Platform-specific compiler flags
if sys.platform.startswith('win'):
    compile_args = ['/O2']
else:
    compile_args = ['-O3', '-Wall', '-Wextra']

# C extension module
csh256_extension = Extension(
    'csh256._csh256',
    sources=['csh256/_csh256.c'],
    extra_compile_args=compile_args,
)

setup(
    ext_modules=[csh256_extension],
)
