"""
This is free and unencumbered software released into the public domain.
For more information, please visit <http://unlicense.org/>.
"""
from pyppi import version
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    description="Python Package index builder",
    author="Tom Barron",
    author_email="tusculum@gmail.com",
    url="... update this ...",
    download_url="... update this ...",
    version=version._v,
    name="pyppi",
)
