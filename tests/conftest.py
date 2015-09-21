"""
pytest fixtures
"""


import os

import pytest


@pytest.fixture(scope='function')
def dicts_gz_path():
    return os.path.join('tests', 'data', 'dictionaries.json.gz')


@pytest.fixture(scope='function')
def dicts_path():
    return os.path.join('tests', 'data', 'dictionaries.json')


@pytest.fixture(scope='function')
def dicts_csv_with_null():
    return os.path.join('tests', 'data', 'with-null.csv')


@pytest.fixture(scope='function')
def dicts_csv_path():
    return os.path.join('tests', 'data', 'dictionaries.csv')
