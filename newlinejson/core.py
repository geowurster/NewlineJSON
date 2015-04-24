"""
Core components for NewlineJSON
"""


import json
import os
from io import StringIO

from .pycompat import string_types
from .pycompat import PY2
from .deprecated import Reader
from .deprecated import Writer


__all__ = ['open', 'Stream', 'load', 'loads', 'dump', 'dumps', 'Reader', 'Writer']


# Need this inside the new open function
builtin_open = open


JSON_LIB = json


def open(path, mode='r', open_args=None, **stream_args):

    """
    Open a file path or file-like object for I/O operations and return a loaded
    `Stream()` instance.


    Parameters
    ----------
    path : str or file
        Input file path or `file` instance.

    mode : str, optional
        I/O mode like 'r', 'w', or 'a'.  Defaults to 'r'.

    open_args : dict or None, optional
        Additional keyword arguments for Python's built-in `open()` function.

    stream_args : **kwargs, optional
        Additional keyword arguments for `Stream()`.


    Returns
    -------
    Stream
    """

    if open_args is None:
        open_args = {}

    if isinstance(path, string_types):
        input_stream = builtin_open(path, **open_args)
    elif hasattr(path, '__iter__'):
        input_stream = path
    else:
        raise TypeError("Path must be a filepath or an iterable file-like object.")

    return Stream(input_stream, mode=mode, **stream_args)


class Stream(object):

    """
    Perform I/O operations on a stream of newline delimited JSON.
    """

    io_modes = ('r', 'w', 'a')

    def __init__(self, stream, mode='r', skip_lines=0, skip_failures=False, linesep=os.linesep,
                 json_lib=None, **stream_args):

        """
        Connect to an open file-like object containing newline delimited JSON.
        This class is the core component of NewlineJSON and behaves similarly
        to a file-like object.

        Three I/O modes are supported: 'r' for reading data, 'a' for appending to
        an existing stream, and 'w' for overwriting any data that may already be
        present in the stream.


        Attributes
        ----------
        closed : bool
            Is the stream open for I/O operations?

        json_lib : module
            The JSON library currently being used for encoding and decoding.

        mode : str
            I/O mode of the `Stream()` instance.

        skip_failures : bool
            Are failures being logged or thrown?

        stream : file-like object
            The underlying file-like object being read from or written to.


        Parameters
        ----------
        stream : file
            An open file-like object for reading or writing.  Object should have
            been opened with a mode that compliments ``mode`` although this is not
            checked to allow support for more customized file handling.

        mode : str, optional
            I/O mode stream should operate in.  Must be 'r', 'a', or 'w'.

        skip_lines : int, optional
            Immediately skip the first N lines of the input file if reading.

        skip_failures : bool, optional
            Normally when a JSON object or string can't be encoded or decoded
            an exception is raised.  Setting ``skip_failures`` to ``True`` causes
            these exceptions to be logged rather than thrown.  See `next()` and
            `write()` for more information about how this is handled.

        linesep : str, optional
            Newline delimiter to write after each line.  Defaults to ``os.linesep``.

        json_lib : module, optional
            The built-in JSON library works fine but is slow.  There are other
            faster implementations that will be used if set via the global
            ``JSON_LIB`` variable or the instance `json_lib` variable.

        stream_args : **stream_args, optional
            Additional keyword arguments for `json_lib.dumps/loads()`.
        """

        global JSON_LIB

        if json_lib is None:
            self.json_lib = JSON_LIB
        else:
            self.json_lib = json_lib

        if mode not in self.io_modes:
            raise ValueError("Mode `%s' is unrecognized: %s"
                             % (mode, ', '.join(self.io_modes)))
        if skip_lines < 0:
            raise ValueError("skip_lines must be > 0")

        self.skip_failures = skip_failures
        self._mode = mode
        self._stream = stream
        self._kwargs = stream_args
        self._is_closed = False
        self._linesep = linesep
        for i in range(skip_lines):
            self.next()

    def __repr__(self):
        return "<%s Stream '%s', mode '%s' at %s>" % (
            "closed" if self.closed else "open",
            getattr(self._stream, 'name', type(self._stream)),
            self.mode,
            hex(id(self))
        )

    @property
    def mode(self):

        """
        Returns the mode `Stream()` was instantiated with.

        Returns
        -------
        str
            I/O mode (r, w, a, etc.)
        """

        return self._mode

    @property
    def stream(self):

        """
        Returns a handle to the underlying file-like object.

        Returns
        -------
        file
        """

        return self._stream

    @property
    def closed(self):

        """
        Reports whether the stream is open for I/O operations.

        Returns
        -------
        bool
            True if closed.
        """

        return self._is_closed

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):

        """
        Returns an iterator that reads, decodes, and returns one line every
        iteration.
        """

        return self

    def next(self):

        """
        Read a line from the underlying file-like object and convert it to JSON.
        If `skip_failures` is `True` then exceptions will be logged rather than
        thrown and each `next()` call will read until it successfully decodes a
        line or until it reaches the end of the file.  `stream_args` will be passed
        to `json_lib.dumps()`. Raises an exception if `Stream()` isn't open for
        reading.

        Raises
        ------
        OSError
            If `Stream()` is not open with mode `r` or `a` or if the instance has
            been closed via `close()`.
        """

        if self._mode != 'r':
            raise OSError("Stream not open for reading")
        elif self.closed:
            raise OSError("Can't operate on a closed stream")

        line = None
        while line is None:
            try:
                line = self.json_lib.loads(next(self._stream))
            except StopIteration as e:
                raise e
            except Exception as e:
                if not self.skip_failures:
                    raise e

        return line

    __next__ = next

    def write(self, obj):

        """
        Write a JSON object to the underlying file-like object.  If `skip_failures`
        is `True` then exceptions will be logged rather than thrown and `stream_args`
        will be passed to `json_lib.dumps()`. Raises an exception if `Stream()`
        isn't open for writing.

        Parameters
        ----------
        obj : list or dict
            An object to encode as JSON and write.


        Raises
        ------
        OSError
            If `Stream()` is not open with mode `w` or if the instance has been
            closed via `close()`.
        """

        if self._mode not in ('w', 'a'):
            raise OSError("Stream not open for writing")
        elif self.closed:
            raise OSError("Can't operate on a closed stream")

        try:
            encoded = self.json_lib.dumps(obj, **self._kwargs)
            if PY2:  # pragma no cover
                encoded = encoded.decode('utf-8')
            return self._stream.write(encoded + self._linesep)
        except Exception as e:
            if not self.skip_failures:
                raise e

    def close(self):

        """
        Close the `Stream()` and its underlying file if it has a `close()`
        method.  Once closed `Stream()` cannot be re-opened.
        """

        if hasattr(self._stream, 'close'):
            self._stream.close()

        self._is_closed = True


def load(f, **stream_args):

    """
    Use `open()` instead.  Provided only to match the builtin `json`
    library's functionality.

    Load an open file-like object into `Stream()`.


    Parameters
    ----------
    f : file
        File-like object open for reading.
    stream_args : **stream_args, optional
        Additional keyword arguments for `Stream()`.
    """

    return Stream(f, **stream_args)


def loads(string, **stream_args):

    """
    Load newline JSON encoded as a string into a `Stream()` instance.


    Parameters
    ----------
    string : str
        Newline JSON encoded as a string.
    stream_args : **stream_args, optional
        Additional keyword arguments for `Stream()`.
    """

    if PY2:  # pragma no cover
        string = string.decode('utf-8')

    return Stream(StringIO(string), **stream_args)


def dump(collection, f, **stream_args):

    """
    Dump a collection of JSON objects into a file.


    Parameters
    ----------
    collection : iterable
        Iterable that produces one JSON object per iteration.
    f : file
        File-like object open for writing.
    stream_args : **stream_args, optional
        Additional keyword arguments for `Stream()`.
    """

    dst = Stream(f, 'w', **stream_args)
    for item in collection:
        dst.write(item)


def dumps(collection, **stream_args):

    """
    Dump a collection of JSON objects into a string.


    Parameters
    ----------
    collection : iterable
        Iterable that produces one JSON object per iteration.
    stream_args : **stream_args, optional
        Additional keyword arguments for `Stream()`.

    Returns
    -------
    str
    """

    with StringIO() as f:
        dst = Stream(f, 'w', **stream_args)
        for item in collection:
            dst.write(item)
        f.seek(0)
        return f.read()
