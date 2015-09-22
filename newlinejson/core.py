"""
Core components for NewlineJSON
"""


import codecs
import json
from io import StringIO
import os
import six
import sys


__all__ = ['open', 'NLJStream', 'load', 'loads', 'dump', 'dumps', 'NLJReader', 'NLJWriter']


JSON_LIB = json


def open(name, mode='r', open_args=None, **kwargs):

    """
    Open a file path or file-like object for I/O operations and return a loaded
    `NLJStream()` instance.

    Parameters
    ----------
    name : str or file
        Input file path or file-like object.  File-like objects are only
        validated by checking for `next/__next__()` and `close()` methods.
    mode : str, optional
        I/O mode.  See `NLJStream()` for a list of options.  Think file-like.
    open_args : dict or None, optional
        Additional keyword arguments for Python's built-in `open()` function.
    kwargs : **kwargs, optional
        Additional keyword arguments for `NLJStream()`.

    Returns
    -------
    NLJStream
    """

    open_args = open_args or {}

    if name == '-' and mode == 'r':
        stream = sys.stdin
    elif name == '-' and mode in ('w', 'a'):
        stream = sys.stdout
    elif isinstance(name, six.string_types):
        open_args.update(mode=mode)
        stream = codecs.open(name, **open_args)
    elif hasattr(name, 'close') or (hasattr(name, '__next__') or hasattr(name, 'next')):
        stream = name
    else:
        raise TypeError(
            "Path must be a filepath, file-like object with .close or .__next__/next, "
            "or '-' for stdin/stdout.")

    if mode == 'r':
        return NLJReader(stream, mode=mode, **kwargs)
    elif mode in ('w', 'a'):
        return NLJWriter(stream, mode=mode, **kwargs)
    else:
        raise ValueError("Invalid mode: {}".format(mode))


class NLJStream(object):

    """
    Baseclass for performing I/O operations on a stream of newline delimited
    JSON.  Implements common file-like object properties and methods
    """

    io_modes = ('r', 'w', 'a')

    def __init__(self, stream, mode='r', skip_failures=False, newline=os.linesep,
                 json_lib=None, **json_args):

        """
        Connect to an open file-like object containing newline delimited JSON.
        This class is the core component of NewlineJSON and behaves similarly
        to a file-like object.

        Three I/O modes are supported:

            r : Read data.
            a : Append data to the end of a file.
            w : Write data and clobber anything that already exists.

        Parameters
        ----------
        stream : file
            An open file-like object for reading or writing.  Object should have
            been opened with a mode that compliments `mode` although this is not
            validated.
        mode : str, optional
            I/O mode stream should operate in.  Must be 'r', 'a', or 'w'.
        skip_failures : bool, optional
            Don't crash when lines can't be encoded or decoded.
        newline : str, optional
            Newline delimiter to write after each line.  Defaults to
            ``os.linesep``.
        json_lib : str or module or object, optional
            The built-in JSON library works fine but is slow.  There are other
            faster implementations that can be used as long as they support
            `json_lib.loads()` and `json_lib.dumps()`.  If not supplied, the
            global `JSON_LIB` will be used, which defaults to `json`.  To
            support some downstream command line applications, this can also
            be a module name as a string, which will be imported in `__init__`.
        json_args : **json_args, optional
            Additional keyword arguments for `json_lib.dumps/loads()`.

        Attributes (aside from the appropriate file-like object properties)
        ----------
        json_lib : module or object
            The JSON library currently being used.
        skip_failures : bool
            Are exceptions on read and write being logged or thrown?
        num_failures : int
            The number of failures encountered thus far.
        """

        global JSON_LIB

        self._json_lib = json_lib or JSON_LIB
        if isinstance(self._json_lib, six.string_types):
            self._json_lib = __import__(self._json_lib)

        if mode not in self.io_modes:
            raise ValueError(
                "Mode '{mode}' is unrecognized - must be one of: {io_modes}".format(
                    mode=mode, io_modes=self.io_modes))

        self.skip_failures = skip_failures
        self._mode = mode
        self._stream = stream
        self._json_args = json_args or {}
        self._linesep = newline
        self._num_failures = 0

    def __repr__(self):
        return "<{io} {cname} '{name}', mode '{mode}' at {id}>".format(
            io="closed" if self.closed else "open",
            cname=self.__class__.__name__,
            name=self.name, mode=self.mode, id=hex(id(self)))

    @property
    def num_failures(self):
        """The number of lines that could not be read or written."""
        return self._num_failures

    @property
    def mode(self):
        """I/O mode - (r, w, a,)"""
        return self._stream.mode

    @property
    def closed(self):
        """Reports whether the stream is open for I/O operations."""
        return self._stream.closed

    @property
    def name(self):
        """Name of underlying file-like object."""
        return self._stream.name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        """Close and flush to disk."""
        self.close()
        if hasattr(self._stream, '__del__'):
            return self._stream.__del__()
        else:
            return None

    def close(self):
        """Close the stream and flush to disk."""
        return self._stream.close()
    
    def flush(self):
        """Flush the buffer to disk."""
        return self._stream.flush()


class NLJReader(NLJStream):

    """
    Read a stream of newline JSON.
    """

    def __iter__(self):
        """Iterate over lines in the input stream."""
        return self

    def __next__(self):

        """
        Read a line from the underlying file-like object and convert it to JSON.

        If skipping failures, then exceptions will be logged rather than
        thrown and each `next()` call will read until it successfully decodes a
        line or until it reaches the end of the file.
        """

        line = None
        while line is None:
            try:
                line = self._json_lib.loads(next(self._stream), **self._json_args)
            except StopIteration:
                raise
            except Exception:
                self._num_failures += 1
                if not self.skip_failures:
                    raise

        return line

    next = __next__


class NLJWriter(NLJStream):

    """
    Write NLJ to a stream.
    """

    def write(self, obj):

        """
        Write a JSON object to the underlying file-like object.  If skipping
        failures then exceptions will be logged rather than thrown.

        Parameters
        ----------
        obj : list or dict
            An object to encode as JSON and write.
        """

        try:
            encoded = self._json_lib.dumps(obj, **self._json_args)
            if six.PY2:
                encoded = encoded.decode('utf-8')
            return self._stream.write(encoded + self._linesep)
        except Exception:
            self._num_failures += 1
            if not self.skip_failures:
                raise


def load(f, **json_args):

    """
    Use `open()` instead.  Provided to match the builtin `json` library's
    functionality.

    Load an open file-like object into `NLJReader()`.

    Parameters
    ----------
    f : file
        File-like object open for reading.
    json_args : **json_args, optional
        Additional keyword arguments for `NLJReader()`.
    """

    return NLJReader(f, **json_args)


def loads(string, **json_args):

    """
    Load a string containing newline JSON into a `NLJReader()`.  Provided to
    match the `json` library's functionality.  This may be more appropriate:

        >>> map(json.loads, string.splitlines())

    Parameters
    ----------
    string : str
        Newline JSON encoded as a string.
    json_args : **json_args, optional
        Additional keyword arguments for `NLJReader()`.
    """

    if six.PY2:  # pragma no cover
        string = string.decode('utf-8')

    return NLJReader(StringIO(string), **json_args)


def dump(collection, f, **json_args):

    """
    Use `open()` instead.  Provided to match the builtin `json` library's
    functionality.
    
    Dump a collection of JSON objects into a file.

    Parameters
    ----------
    collection : iter
        Iterable that produces one JSON object per iteration.
    f : file
        File-like object open for writing.
    json_args : **json_args, optional
        Additional keyword arguments for `NLJWriter()`.
    """

    dst = NLJWriter(f, 'w', **json_args)
    try:
        for item in collection:
            dst.write(item)
    finally:
        dst.close()


def dumps(collection, **json_args):

    """
    Dump a collection of JSON objects into a string.  Primarily included to
    match the `json` library's functionality.  This may be more appropriate:

        >>> os.linesep.join(list(map(json.dumps, collection))

    Parameters
    ----------
    collection : iter
        Iterable that produces one JSON object per iteration.
    json_args : **json_args, optional
        Additional keyword arguments for `NLJWriter()`.

    Returns
    -------
    str
    """

    with StringIO() as f:
        with NLJWriter(f, 'w', **json_args) as dst:
            for item in collection:
                dst.write(item)
            f.seek(0)
            return f.read()
