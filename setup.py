#!/usr/bin/env python


"""
Setup script for NewlineJSON
"""


from itertools import chain
import os
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


# https://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['tests']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, because outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


with open('README.rst') as f:
    readme = f.read().strip()


version = None
author = None
email = None
source = None
with open(os.path.join('newlinejson', '__init__.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            version = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__author__'):
            author = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__email__'):
            email = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif line.strip().startswith('__source__'):
            source = line.split('=')[1].strip().replace('"', '').replace("'", '')
        elif None not in (version, author, email, source):
            break


extras_require = {
    'dev': [
        'pytest',
        'pytest-cov'
    ],
    'cli': ['click>=3.0']
}
extras_require.update(all=list(chain(extras_require.values())))


setup(
    name='NewlineJSON',
    author=author,
    author_email=email,
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    cmdclass={'test': PyTest},
    description="Streaming newline delimited JSON I/O with transparent compression",
    extras_require=extras_require,
    include_package_data=True,
    install_requires=[
        'six'
    ],
    keywords='streaming newline delimited json',
    license="New BSD",
    long_description=readme,
    packages=find_packages(exclude=['tests']),
    url=source,
    version=version,
    zip_safe=True
)
