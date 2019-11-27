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
    name="pyppi",
    version=version._v,
    description="Python Package index builder",
    author="Tom Barron",
    author_email="tusculum@gmail.com",
    packages=['pyppi'],
    entry_points = {
        'console_scripts': ['pyppi=pyppi.__main__:main']
    },
    data_files=[
        ('pkg_data/pyppi/info', [
                                 './LICENSE',
                                 './README.md',
                                 'CHANGELOG.md',
                                ]),
    ],
    url="... update this ...",
    download_url="... update this ...",
)
