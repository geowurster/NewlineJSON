"""
I/O components for NewlineJSON
"""


import json
import os
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO


__all__ = ['open', 'Stream', 'load', 'loads', 'dump', 'dumps']


# Need this inside the new open function
builtin_open = open


JSON_LIB = json


def open(path, mode='r', cmode=None, compression=None, co=None, oo=None, **kwargs):

    """
    Open a file path (or stdin) for I/O operations and return a `Stream()` instance.

    Several compression formats are supported transparently and are auto-detected
    based on the input file-path.  See the global `COMPRESSION_FORMATS` variable
    for a dictionary of supported format names and their associated file extensions.
    Auto-detection is disabled if `path` is an instance of `file` or if the
    `compression` option is `False`.  If a path to a compressed file is given
    but auto-detection continually fails, explicitly specify `compression=name`.

    Some compression formats support more than just modes 'r', 'w', and 'a'.
    By default the I/O mode passed to the compression library is `mode` but if
    a special compression mode is desired use `cmode` as long as it complements
    `mode`.  Using `mode='r'` and `cmode='w'` will yield a locked datasource
    and probably some weird exceptions.  Additional kwargs or 'compression
    options' can be passed to the compression library with `co={'name': 'val'}`.
    If no compression is used `co` is passed to Python's builtin `open()` function
    as `**kwargs`.

    Parameters
    ----------
    path : str or file
        Input file path or `file` instance.
    mode : str, optional
        I/O mode like 'r', 'w', or 'a'.  Defaults to 'r'.
    cmode : str, optional
        I/O mode for compression library.  Defaults to `mode`.
    compression: str or None or False, optional
        Name of compression library to use.  If `None` compression will be
        auto-detected from the file path or `name` attribute if `path` is an
        instance of `file`.  Use `False` to disable auto-detection.
    co : dict or None, optional
        Additional keyword arguments for the compression library.
    oo : dict or None, optional
        Additional keyword arguments for Python's built-in `open()` function.
    kwargs : **kwargs, optional
        Additional keyword arguments for `Stream()`.

    Returns
    -------
    Stream
    """

    if cmode is None:
        cmode = mode
    if co is None:
        co = {}
    if oo is None:
        oo = {}

    # Compression was specified or should be auto-detected
    if compression is not False:

        # Try to get compression from the extension
        if compression is None:
            if (hasattr(path, 'next') or hasattr(path, '__next__')) and hasattr(path, 'name'):
                _prefix = path.name
            else:
                _prefix = path
            _c_test = _prefix.rpartition('.')[-1]
            if _c_test not in ('json', 'nljson', 'newlinejson'):
                compression = _c_test

    if compression:

        # Instantiate a compression driver
        if compression in ('gz', 'gzip'):
            import gzip
            stream = gzip.open(path, cmode, **co)
        elif compression in ('bz2', 'bzip2'):
            import bz2
            stream = bz2.BZ2File(path, cmode, **co)
        else:
            raise ValueError("Compression `%s' is unsupported")

    # Input path is actually a file-like object, which can just be dropped into Stream()
    elif hasattr(path, 'next') or hasattr(path, '__next__'):
        stream = path

    # Input path is a file-path and needs to be opened
    else:
        stream = builtin_open(path, mode, **oo)

    return Stream(stream, mode=mode, **kwargs)


class Stream(object):

    """
    Perform I/O operations on a stream of newline delimited JSON.
    """

    modes = ('r', 'w', 'a')

    def __init__(self, stream, mode='r', skip_lines=0, skip_failures=False, linesep=os.linesep,
                 json_lib=JSON_LIB, **kwargs):

        """
        Connect to an open file-like object containing string encoded newline JSON.
        Use `open()` to directly interact with files on disk and different various
        compression formats.

        Three I/O modes are supported: 'r' for reading data, 'a' for appending to
        an existing stream, and 'w' for overwriting any data that may already be
        present in the stream.

        Parameters
        ----------
        stream : file
            An open file-like object for reading and writing.  Object should have
            been opened with a mode that compliments `mode` although this is not
            checked to allow support for compression specific I/O modes.
        mode : str, optional
            I/O mode stream should operate in.  Must be 'r', 'a', or 'w'.
        skip_lines : int, optional
            Immediately skip the first N lines of the input file if reading.
        skip_failures : bool, optional
            Normally when a JSON object or string can't be encoded or decoded
            an exception is raised.  Setting `skip_failures` to `True` causes
            these exceptions to be logged rather than thrown.  See `next()` and
            `write()` for more information about how this is handled.
        linesep : str, optional
            Newline delimiter to write after each line.  Defaults to `os.linesep`.
        json_lib : module, optional
            The built-in JSON library works fine but is slow.  There are other
            faster implementations that will be used if set via the global
            `JSON_LIB` variable or the instance `json_lib` variable.
        kwargs : **kwargs, optional
            Additional keyword arguments for `json_lib.dumps/loads()`.
        """

        if mode not in self.modes:
            raise ValueError("Mode `%s' is unrecognized: %s" % ', '.join(self.modes))
        if skip_lines < 0:
            raise ValueError("skip_lines must be > 0")

        self.json_lib = json_lib
        self.skip_failures = skip_failures
        self._mode = mode
        self._stream = stream
        self._kwargs = kwargs
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
        line or until it reaches the end of the file.  `kwargs` will be passed
        to `json_lib.dumps()`. Raises an exception if `Stream()` isn't open for
        reading.

        Raises
        ------
        IOError
            If `Stream()` is not open with mode `r` or `a` or if the instance has
            been closed via `close()`.
        """

        if self._mode != 'r':
            raise IOError("Stream not open for reading")
        elif self.closed:
            raise IOError("Can't operate on a closed stream")

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
        is `True` then exceptions will be logged rather than thrown and `kwargs`
        will be passed to `json_lib.dumps()`. Raises an exception if `Stream()`
        isn't open for writing.

        Parameters
        ----------
        obj : list or dict
            An object to encode as JSON and write.

        Raises
        ------
        IOError
            If `Stream()` is not open with mode `w` or if the instance has been
            closed via `close()`.
        """

        if self._mode not in ('w', 'a'):
            raise IOError("Stream not open for writing")
        elif self.closed:
            raise IOError("Can't operate on a closed stream")

        try:
            return self._stream.write(self.json_lib.dumps(obj, **self._kwargs) + self._linesep)
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


def load(f, **kwargs):

    """
    Load an open file into `Stream()`.

    Parameters
    ----------
    f : file
        File-like object open for reading.
    kwargs : **kwargs, optional
        Additional keyword arguments for `Stream()`.
    """

    return Stream(f, **kwargs)


def loads(string, **kwargs):

    """
    Load newline JSON encoded as a string into a `Stream()` instance.

    Parameters
    ----------
    string : str
        Newline JSON encoded as a string.
    kwargs : **kwargs, optional
        Additional keyword arguments for `Stream()`.
    """

    with StringIO(string) as f:
        return Stream(f, **kwargs)


def dump(obj, f, **kwargs):

    """
    Dump a collection of JSON objects into a file.

    Parameters
    ----------
    obj : iterable
        Object that produces one JSON object per iteration.
    f : file
        File-like object open for writing.
    kwargs : **kwargs, optional
        Additional keyword arguments for `Stream()`.
    """

    dst = Stream(f, 'w', **kwargs)
    for item in obj:
        dst.write(item)


def dumps(obj, **kwargs):

    """
    Dump a collection of JSON objects into a string.

    Parameters
    ----------
    obj : iterable
        Object that produces one JSON object per iteration.
    kwargs : **kwargs, optional
        Additional keyword arguments for `Stream()`.

    Returns
    -------
    str
    """

    with StringIO() as f:
        dst = Stream(f, 'w', **kwargs)
        for item in obj:
            dst.write(item)
        f.seek(0)
        return f.read()
