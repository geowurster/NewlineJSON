"""
Unittests for newlinejson.core
"""


import json
import itertools
import tempfile

from nose.tools import assert_raises
try:
    import ujson
except ImportError:
    ujson = None

import newlinejson.pycompat
import newlinejson as nlj
from . import sample_data


def compare_iterables(collection1, collection2):
    for i1, i2 in zip(collection1, collection2):
        assert i1 == i2, "%s != %s" % (i1, i2)
    return True


def test_compare_iterables():
    assert compare_iterables('abc', 'abc')
    with assert_raises(AssertionError):
        compare_iterables((1, 2, 3), 'a')


def test_standard():

    with nlj.open(sample_data.DICTS_JSON_PATH) as actual, \
            open(sample_data.DICTS_JSON_PATH) as expected:

        for e_line, a_line in zip(expected, actual):
            assert json.loads(e_line) == a_line


def test_read_file_obj():

    with open(sample_data.DICTS_JSON_PATH) as f, \
            nlj.open(sample_data.DICTS_JSON_PATH) as expected:
        compare_iterables(expected, nlj.open(f))


def test_round_robin():
    with nlj.open(sample_data.DICTS_JSON_PATH) as dicts, \
        nlj.open(sample_data.LISTS_JSON_PATH) as lines, \
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
    with open(sample_data.MIXED_JSON_PATH) as f, \
            nlj.open(sample_data.MIXED_JSON_PATH) as expected:
        compare_iterables(nlj.load(f), expected)


def test_loads():

    with nlj.open(sample_data.MIXED_JSON_PATH) as expected, \
            open(sample_data.MIXED_JSON_PATH) as f:

        actual = nlj.loads(f.read())

        assert isinstance(expected, nlj.Stream) and isinstance(actual, nlj.Stream)

        for attr in ('json_lib', 'skip_failures', 'mode', 'closed'):
            assert getattr(expected, attr) == getattr(actual, attr), attr

        compare_iterables(expected, actual)


def test_dump():

    with open(sample_data.LISTS_JSON_PATH) as f:
        expected = f.read()

    with nlj.open(sample_data.LISTS_JSON_PATH) as src, \
            tempfile.NamedTemporaryFile(mode='r+') as f:
        nlj.dump(src, f)
        f.seek(0)
        actual = f.read()

    assert expected == actual


def test_dumps():

    with open(sample_data.DICTS_JSON_PATH) as f:
        expected = f.read()

    with nlj.open(sample_data.DICTS_JSON_PATH) as src:
        actual = nlj.dumps(src)

    for obj in (expected, actual):
        assert isinstance(obj, nlj.pycompat.string_types)

    compare_iterables(nlj.loads(expected), nlj.loads(actual))


def test_open_invalid_object():
    with assert_raises(TypeError):
        nlj.open(1)


def test_stream_invalid_mode():
    with assert_raises(ValueError):
        with nlj.open(sample_data.DICTS_JSON_PATH, mode='_') as src:
            pass


def test_negative_skiplines():
    with assert_raises(ValueError):
        with nlj.open(sample_data.MIXED_JSON_PATH, skip_lines=-1) as src:
            pass


def test_skiplines():
    sl = 2
    with open(sample_data.MIXED_JSON_PATH) as f, \
            nlj.open(sample_data.MIXED_JSON_PATH, skip_lines=sl) as actual:
        for i in range(sl):
            next(f)
        compare_iterables(nlj.Stream(f), actual)


def test_attributes():
    # stream
    with nlj.open(sample_data.DICTS_JSON_PATH) as src:
        assert hasattr(src.stream, 'read')
        assert src.stream.mode == src.mode

    # __repr__
    with nlj.open(sample_data.DICTS_JSON_PATH) as src:
        assert isinstance(repr(src), nlj.pycompat.string_types)
        assert 'open' in repr(src) and 'Stream' in repr(src) and src.mode in repr(src)
    assert 'closed' in repr(src) and 'Stream' in repr(src) and src.mode in repr(src)


def test_open_no_with_statement():
    s = nlj.open(sample_data.DICTS_JSON_PATH)
    next(s)
    s.close()


def test_io_clash():

    # Trying to read from a stream that is opened in write mode
    with assert_raises(OSError):
        with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
            next(src)

    # Trying to read from a closed stream
    with nlj.open(sample_data.DICTS_JSON_PATH) as src:
        pass
    with assert_raises(OSError):
        next(src)

    # Trying to write to a stream opened in read mode
    with nlj.open(tempfile.NamedTemporaryFile(mode='w')) as dst:
        with assert_raises(OSError):
            dst.write([])

    # Trying to write to a closed stream
    with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as dst:
        pass
    with assert_raises(OSError):
        dst.write([])


def test_read_write_exception():
    # Write a non-JSON serializable object
    with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
        with assert_raises(TypeError):
            src.write(tuple)
    # Read malformed JSON
    with nlj.open(tempfile.NamedTemporaryFile(mode='r+')) as src:
        src.stream.write('{')
        src.stream.seek(0)
        with assert_raises((TypeError, ValueError
                            )):
            next(src)


def test_skip_failures_write():
    with nlj.open(sample_data.DICTS_JSON_PATH) as src, nlj.open(tempfile.NamedTemporaryFile(
            mode='w'), 'w', skip_failures=True) as dst:
        dst.write(next(src))
        dst.write(next(src))
        dst.write(nlj)
        for line in src:
            dst.write(line)


def test_declare_json_lib():
    jlib = 'something'
    with nlj.open(sample_data.DICTS_JSON_PATH, json_lib=jlib) as src:
        assert src.json_lib == jlib


# if ujson is not None:
#     def test_round_robin_with_ujson():
#         nlj.core.JSON_LIB = ujson
#         with nlj.open(sample_data.MIXED_JSON_PATH) as src, \
#                 nlj.open(tempfile.NamedTemporaryFile(mode='r+'), 'w') as dst:
#
#             assert src.json_lib == ujson
#             assert dst.json_lib == ujson
#
#             for line in src:
#                 dst.write(line)
#             dst.stream.seek(0)
#             src.stream.seek(0)
#             compare_iterables(src, nlj.loads(dst.stream.read()))
#         nlj.core.JSON_LIB = json
#         assert nlj.core.JSON_LIB == json
