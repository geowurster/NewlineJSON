"""
Unittests for newlinejson.io
"""


import json
import os
import tempfile

import pytest
import six

import newlinejson as nlj


def test_standard(dicts_path):

    with nlj.open(dicts_path) as actual:
        with open(dicts_path) as expected:
            for e_line, a_line in zip(expected, actual):
                assert json.loads(e_line) == a_line


def test_read_file_obj(dicts_path, compare_iter):

    with open(dicts_path) as f:
        with nlj.open(dicts_path) as expected:
            with nlj.open(f) as actual:
                compare_iter(expected, actual)


def test_open_invalid_object():
    with pytest.raises(TypeError):
        nlj.open(1)


def test_stream_invalid_mode(dicts_path):
    with pytest.raises(ValueError):
        with nlj.open(dicts_path, mode='_') as src:
            pass


def test_attributes(dicts_path):
    with nlj.open(dicts_path) as src:
        assert src.num_failures is 0
        assert src.mode == 'r'
        assert not src.closed
        assert src.name == dicts_path
        assert 'open' in repr(src) and 'r' in repr(src)
    assert 'closed' in repr(src)


def test_open_no_with_statement(dicts_path):
    s = nlj.open(dicts_path)
    next(s)
    s.close()


def test_io_clash(dicts_path):

    # Trying to read from a stream that is opened in write mode
    with pytest.raises(TypeError):
        with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
            next(src)

    # Trying to read from a closed stream
    with nlj.open(dicts_path) as src:
        pass
    with pytest.raises(ValueError):
        next(src)

    # Trying to write to a stream opened in read mode
    with nlj.open(tempfile.NamedTemporaryFile(mode='w')) as dst:
        with pytest.raises(AttributeError):
            dst.write([])

    # Trying to write to a closed stream
    with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as dst:
        pass
    with pytest.raises(ValueError):
        dst.write([])


def test_read_write_exception():
    # Write a non-JSON serializable object
    with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w') as src:
        with pytest.raises(TypeError):
            src.write(tuple)
    # Read malformed JSON
    with nlj.open(tempfile.NamedTemporaryFile(mode='r+')) as src:
        src._stream.write('{')
        src._stream.seek(0)
        with pytest.raises((TypeError, ValueError)):
            next(src)


def test_skip_failures_write(dicts_path):
    with nlj.open(dicts_path) as src:
        with nlj.open(tempfile.NamedTemporaryFile(mode='w'), 'w', skip_failures=True) as dst:
            dst.write(next(src))
            dst.write(next(src))
            dst.write(nlj)
            for line in src:
                dst.write(line)


def test_declare_json_lib(dicts_path):
    jlib = 'something'
    with pytest.raises(ImportError):
        with nlj.open(dicts_path, json_lib=jlib) as src:
            pass


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
        with nlj.open('whatever', mode='bad_mode'):
            pass


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
    with tempfile.NamedTemporaryFile(mode='r+') as f:
        with nlj.open(f.name, 'w', skip_failures=True) as src:
            assert src.num_failures is 0
            src.write(json)
            src.write(src)
            assert src.num_failures is 2


def test_import_json_lib():
    dst = nlj.open(six.moves.StringIO(), json_lib='json')
    assert dst._json_lib == json


def test_flush(tmpdir):
    fp = str(tmpdir.mkdir('test').join('data.json'))
    with nlj.open(fp, 'w') as dst:
        dst.write({'field1': None})
        dst.flush()
    with nlj.open(fp) as src:
        assert next(src) == {'field1': None}


def test_open_bad_mode(dicts_path):
    # These trigger errors in slightly different but very related lines
    with pytest.raises(ValueError):
        with nlj.open(dicts_path, 'bad-mode') as src:
            pass
    with pytest.raises(ValueError):
        with nlj.open(dicts_path, 'rb') as src:
            pass
