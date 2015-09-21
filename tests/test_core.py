"""
Unittests for newlinejson.core
"""


import json
import itertools
import os
import tempfile

import pytest
import six

import newlinejson as nlj


def compare_iterables(collection1, collection2):
    for i1, i2 in zip(collection1, collection2):
        assert i1 == i2, "%s != %s" % (i1, i2)
    return True


def test_compare_iterables():
    assert compare_iterables('abc', 'abc')
    with pytest.raises(AssertionError):
        compare_iterables((1, 2, 3), 'a')


def test_standard(dicts_path):

    with nlj.open(dicts_path) as actual, \
            open(dicts_path) as expected:

        for e_line, a_line in zip(expected, actual):
            assert json.loads(e_line) == a_line


def test_read_file_obj(dicts_path):

    with open(dicts_path) as f, \
            nlj.open(dicts_path) as expected:
        compare_iterables(expected, nlj.open(f))


def test_dumps(dicts_path):

    with open(dicts_path) as f:
        expected = f.read()

    with nlj.open(dicts_path) as src:
        actual = nlj.dumps(src)

    for obj in (expected, actual):
        assert isinstance(obj, six.string_types)

    compare_iterables(nlj.loads(expected), nlj.loads(actual))


def test_open_invalid_object():
    with pytest.raises(TypeError):
        nlj.open(1)


def test_stream_invalid_mode(dicts_path):
    with pytest.raises(ValueError):
        with nlj.open(dicts_path, mode='_') as src:
            pass


def test_negative_skiplines(dicts_path):
    with pytest.raises(ValueError):
        nlj.open(dicts_path, skip_lines=-1)


def test_skiplines(dicts_path):
    sl = 2
    with open(dicts_path) as f, \
            nlj.open(dicts_path, skip_lines=sl) as actual:
        for i in range(sl):
            next(f)
        compare_iterables(nlj.NLJStream(f), actual)


def test_attributes(dicts_path):
    # stream
    with nlj.open(dicts_path) as src:
        assert hasattr(src.stream, 'read')
        assert src.stream.mode == src.mode

    # __repr__
    with nlj.open(dicts_path) as src:
        assert isinstance(repr(src), six.string_types)
        assert 'open' in repr(src) and 'Stream' in repr(src) and src.mode in repr(src)
    assert 'closed' in repr(src) and 'Stream' in repr(src) and src.mode in repr(src)


def test_open_no_with_statement(dicts_path):
    s = nlj.open(dicts_path)
    next(s)
    s.close()


def test_io_clash(dicts_path):

    # Trying to read from a stream that is opened in write mode
    with pytest.raises(OSError):
        with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
            next(src)

    # Trying to read from a closed stream
    with nlj.open(dicts_path) as src:
        pass
    with pytest.raises(OSError):
        next(src)

    # Trying to write to a stream opened in read mode
    with nlj.open(tempfile.NamedTemporaryFile(mode='w')) as dst:
        with pytest.raises(OSError):
            dst.write([])

    # Trying to write to a closed stream
    with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as dst:
        pass
    with pytest.raises(OSError):
        dst.write([])


def test_read_write_exception():
    # Write a non-JSON serializable object
    with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
        with pytest.raises(TypeError):
            src.write(tuple)
    # Read malformed JSON
    with nlj.open(tempfile.NamedTemporaryFile(mode='r+')) as src:
        src.stream.write('{')
        src.stream.seek(0)
        with pytest.raises((TypeError, ValueError
                            )):
            next(src)


def test_skip_failures_write(dicts_path):
    with nlj.open(dicts_path) as src, nlj.open(tempfile.NamedTemporaryFile(
            mode='w'), 'w', skip_failures=True) as dst:
        dst.write(next(src))
        dst.write(next(src))
        dst.write(nlj)
        for line in src:
            dst.write(line)


def test_declare_json_lib(dicts_path):
    jlib = 'something'
    with nlj.open(dicts_path, json_lib=jlib) as src:
        assert src.json_lib == jlib


def test_write():
    expected = {'line': 'val'}
    with tempfile.NamedTemporaryFile(mode='r+') as f:
        with nlj.open(f.name, 'w') as dst:
            dst.write(expected)
        f.seek(0)
        with nlj.open(f.name) as src:
            assert next(src) == expected


def test_stream_bad_io_mode():
    with pytest.raises(ValueError):
        nlj.core.NLJStream(tempfile.TemporaryFile(), mode='bad_mode')


def test_read_num_failures():
    with tempfile.NamedTemporaryFile(mode='r+') as f:
        f.write('{' + os.linesep + ']')
        f.seek(0)
        with nlj.open(f.name, skip_failures=True) as src:
            assert src.num_failures is 0
            for row in src:
                pass
            assert src.num_failures is 2


def test_write_num_failures():
    with tempfile.NamedTemporaryFile(mode='r+') as f, \
            nlj.open(f.name, 'w', skip_failures=True) as src:
        assert src.num_failures is 0
        src.write(json)
        src.write(src)
        assert src.num_failures is 2
