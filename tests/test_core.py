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
from . import data


def compare_iterables(collection1, collection2):
    for i1, i2 in zip(collection1, collection2):
        assert i1 == i2, "%s != %s" % (i1, i2)
    return True


def test_compare_iterables():
    assert compare_iterables('abc', 'abc')
    with pytest.raises(AssertionError):
        compare_iterables((1, 2, 3), 'a')


def test_standard():

    with nlj.open(data.DICTS_JSON_PATH) as actual, \
            open(data.DICTS_JSON_PATH) as expected:

        for e_line, a_line in zip(expected, actual):
            assert json.loads(e_line) == a_line


def test_read_file_obj():

    with open(data.DICTS_JSON_PATH) as f, \
            nlj.open(data.DICTS_JSON_PATH) as expected:
        compare_iterables(expected, nlj.open(f))


def test_round_robin():
    with nlj.open(data.DICTS_JSON_PATH) as dicts, \
        nlj.open(data.LISTS_JSON_PATH) as lines, \
            nlj.open(tempfile.NamedTemporaryFile(mode='r+'), 'w') as dst:
        for line in itertools.chain(*(dicts, lines)):
            dst.write(line)

        dicts._stream.seek(0)
        lines._stream.seek(0)
        dst._stream.seek(0)

        expected = nlj.loads(dicts._stream.read() + lines._stream.read())
        actual = nlj.loads(dst._stream.read())

        compare_iterables(expected, actual)


def test_load():
    with open(data.MIXED_JSON_PATH) as f, \
            nlj.open(data.MIXED_JSON_PATH) as expected:
        compare_iterables(nlj.load(f), expected)


def test_loads():

    with nlj.open(data.MIXED_JSON_PATH) as expected, \
            open(data.MIXED_JSON_PATH) as f:

        actual = nlj.loads(f.read())

        assert isinstance(expected, nlj.NewlineJSONStream) \
               and isinstance(actual, nlj.NewlineJSONStream)

        for attr in ('json_lib', 'skip_failures', 'mode', 'closed'):
            assert getattr(expected, attr) == getattr(actual, attr), attr

        compare_iterables(expected, actual)


def test_dump():

    with open(data.LISTS_JSON_PATH) as f:
        expected = f.read()

    with nlj.open(data.LISTS_JSON_PATH) as src, \
            tempfile.NamedTemporaryFile(mode='r+') as f:
        nlj.dump(src, f)
        f.seek(0)
        actual = f.read()

    assert expected == actual


def test_dumps():

    with open(data.DICTS_JSON_PATH) as f:
        expected = f.read()

    with nlj.open(data.DICTS_JSON_PATH) as src:
        actual = nlj.dumps(src)

    for obj in (expected, actual):
        assert isinstance(obj, six.string_types)

    compare_iterables(nlj.loads(expected), nlj.loads(actual))


def test_open_invalid_object():
    with pytest.raises(TypeError):
        nlj.open(1)


def test_stream_invalid_mode():
    with pytest.raises(ValueError):
        with nlj.open(data.DICTS_JSON_PATH, mode='_') as src:
            pass


def test_negative_skiplines():
    with pytest.raises(ValueError):
        with nlj.open(data.MIXED_JSON_PATH, skip_lines=-1) as src:
            pass


def test_skiplines():
    sl = 2
    with open(data.MIXED_JSON_PATH) as f, \
            nlj.open(data.MIXED_JSON_PATH, skip_lines=sl) as actual:
        for i in range(sl):
            next(f)
        compare_iterables(nlj.NewlineJSONStream(f), actual)


def test_attributes():
    # stream
    with nlj.open(data.DICTS_JSON_PATH) as src:
        assert hasattr(src.stream, 'read')
        assert src.stream.mode == src.mode

    # __repr__
    with nlj.open(data.DICTS_JSON_PATH) as src:
        assert isinstance(repr(src), six.string_types)
        assert 'open' in repr(src) and 'Stream' in repr(src) and src.mode in repr(src)
    assert 'closed' in repr(src) and 'Stream' in repr(src) and src.mode in repr(src)


def test_open_no_with_statement():
    s = nlj.open(data.DICTS_JSON_PATH)
    next(s)
    s.close()


def test_io_clash():

    # Trying to read from a stream that is opened in write mode
    with pytest.raises(OSError):
        with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
            next(src)

    # Trying to read from a closed stream
    with nlj.open(data.DICTS_JSON_PATH) as src:
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


def test_skip_failures_write():
    with nlj.open(data.DICTS_JSON_PATH) as src, nlj.open(tempfile.NamedTemporaryFile(
            mode='w'), 'w', skip_failures=True) as dst:
        dst.write(next(src))
        dst.write(next(src))
        dst.write(nlj)
        for line in src:
            dst.write(line)


def test_declare_json_lib():
    jlib = 'something'
    with nlj.open(data.DICTS_JSON_PATH, json_lib=jlib) as src:
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
        nlj.core.NewlineJSONStream(tempfile.TemporaryFile(), mode='bad_mode')


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
