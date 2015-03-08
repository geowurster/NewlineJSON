#!/usr/bin/env python


"""
Setup script for NewlineJSON
"""


import os
import setuptools


with open('README.rst') as f:
    readme = f.read().strip()


with open('LICENSE.txt') as f:
    license = f.read().strip()


version = None
author = None
email = None
source = None
with open('newlinejson.py') as f:
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


setuptools.setup(
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
    description="Streaming newline delimited JSON I/O",
    include_package_data=True,
    keywords='streaming newline delimited json',
    license=license,
    long_description=readme,
    name='NewlineJSON',
    py_modules=['newlinejson'],
    url=source,
    version=version,
    zip_safe=True
)
