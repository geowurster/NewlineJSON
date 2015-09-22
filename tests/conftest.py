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
def dicts_csv_with_null_path():
    return os.path.join('tests', 'data', 'with-null.csv')


@pytest.fixture(scope='function')
def dicts_csv_path():
    return os.path.join('tests', 'data', 'dictionaries.csv')


@pytest.fixture(scope='function')
def dicts_with_null_path():
    return os.path.join('tests', 'data', 'with-null.json')


@pytest.fixture(scope='function')
def compare_iter():
    def compare_iterables(collection1, collection2):
        for i1, i2 in zip(collection1, collection2):
            assert i1 == i2, "%s != %s" % (i1, i2)
    return compare_iterables


def test_compare_iterables(compare_iter):
    compare_iter('abc', 'abc')
    with pytest.raises(AssertionError):
        compare_iter((1, 2, 3), 'a')
