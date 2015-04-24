"""
DEPRECATED - will be removed before v1.0

Old newlinejson.py stripped down to include only the bare-necessities to prevent
anything from breaking.
"""


import json
import os
try:
    from io import StringIO
except ImportError:  # pragma no cover
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
import sys
import warnings


JSON = json


# Python 2/3 compatibility
PY3 = sys.version_info[0] is 3
if PY3:  # pragma no cover
    STR_TYPES = (str)
else:  # pragma no cover
    STR_TYPES = (str, unicode)


class Reader(object):

    """
    Stream newline delimited JSON.
    """

    def __init__(self, f, skip_lines=0, skip_failures=False, skip_empty=True, empty_val=None, fail_val=None,
                 json_lib=None, **kwargs):

        """
        Read a file containing newline delimited JSON.

        Parameters
        ---------
        empty_val : anything, optional
            Value to return if `skip_empty=False` - since an empty line has no
            corresponding JSON object, something must be returned.
        f : file
            Handle to an open file object that is open for reading.
        fail_val : anything, optional
            Value to return if `skip_failures=True` and a line cannot be decoded.
        json_lib : module, optional
            Specify which JSON library to use for this instance
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.JSON.loads()`.
        skip_empty : bool, optional
            If True, skip empty lines.
        skip_failures : bool, optional
            If True, exceptions thrown by `newlinejson.JSON.loads()` will be
            suppressed and the offending line will be ignored.
        skip_lines : int, optional
            Number of lines to immediately skip with `next(f)`

        Attributes
        ----------
        f : file
            Handle to the input file.
        fail_val : anything
            Value being returned from `next()` when a failure is encountered.
        failures : int
            Number of failures encountered.
        json_lib : module
            JSON library currently being used for decoding.
        kwargs : **kwargs
            Keyword args being passed to `self.json_lib.loads()`.
        line_num : int
            Line number that was most recently read.
        skip_lines : int
            Number of lines that were skipped on instantiation.
        skip_empty : bool
            Are empty lines being skipped?
        skip_failures : bool
            Are failures being skipped?
        """

        warnings.warn("`newlinejson.Reader()` is deprecated and will be removed before "
                      "v1.0.  Switch to `newlinejson.open()`.", FutureWarning, stacklevel=2)

        self._f = f
        self.skip_lines = skip_lines
        self.skip_failures = skip_failures
        self.skip_empty = skip_empty
        self.fail_val = fail_val
        self.empty_val = empty_val
        self.kwargs = kwargs
        self._failures = 0
        self._line_num = 0
        if json_lib is None:
            self.json_lib = JSON
        else:
            self.json_lib = json_lib
        for i in range(skip_lines):
            self.next()

    def __iter__(self):
        return self

    @property
    def f(self):

        """
        Handle to the file-like object from which lines are being read.

        Returns
        -------
        file
        """

        return self._f

    @property
    def failures(self):

        """
        Number of failures encountered.

        Returns
        -------
        int
        """

        return self._failures

    @classmethod
    def from_string(cls, string, container=StringIO, **kwargs):

        """
        Create a `Reader()` instance with a string containing newline delimited
        JSON instead of a file-like object.

        Parameters
        ----------
        container : StringIO, optional
            Class used to convert a string to a file-like object.
        kwargs : **kwargs, optional
            Keyword arguments for `Reader()`.
        string : str
            Contains newline delimited JSON.

        Returns
        -------
        Reader
        """

        if not PY3:  # pragma no cover
            string = string.decode()

        return cls(container(string), **kwargs)

    def _readline(self):

        """
        Handle Python3 `__next__()` vs. `next()`.

        Returns
        -------
        str
            The next stripped line from the file.
        """

        self._line_num += 1
        return next(self._f).strip()

    def next(self):

        """
        Read and decode the next non-blank line in the file.

        If `skip_failures` is `True` then the next non-blank successfully
        decoded line is returned.

        Returns
        -------
        dict
        """

        try:

            row = self._readline()
            if self.skip_empty:
                while not row:
                    row = self._readline()
            elif not row:
                return self.empty_val

            return self.json_lib.loads(row, **self.kwargs)

        except ValueError as e:
            self._failures += 1
            if not self.skip_failures:
                raise e
            else:
                return self.fail_val

    __next__ = next


class Writer(object):

    """
    Write newline delimited JSON.
    """

    def __init__(self, f, skip_failures=False, delimiter=os.linesep, json_lib=None, **kwargs):

        """
        Read a file containing newline delimited JSON.

        Parameters
        ---------
        delimiter : str, optional
            Newline character to be written after every row.
        f : file
            Handle to an open writable file-like object.
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.JSON.dumps()`.
        skip_failures : bool, optional
            If True, exceptions thrown by `newlinejson.JSON.dumps()` will be
            suppressed and the offending line will be ignored.

        Attributes
        ----------
        delimiter : str
            Newline character.
        f : file
            Handle to the input file.
        failures : int
            Number of failures encountered.
        json_lib : module
            JSON library currently being used for decoding
        kwargs : dict
            Keyword args being passed to `self.json_lib.dumps()`.
        line_num : int
            Line number that was most recently written.
        skip_failures : bool
            Are failures being skipped?
        """

        warnings.warn("`newlinejson.Writer()` is deprecated and will be removed before "
                      "v1.0.  Switch to `newlinejson.open()`.", FutureWarning, stacklevel=2)

        self._f = f
        self.skip_failures = skip_failures
        self.delimiter = delimiter
        self.kwargs = kwargs
        self._line_num = 0
        self._failures = 0
        if json_lib is None:
            self.json_lib = JSON
        else:
            self.json_lib = json_lib

    @property
    def f(self):

        """
        Handle to the file-like object from which lines are being read.

        Returns
        -------
        file
        """

        return self._f

    @property
    def failures(self):

        """
        Number of failures encountered.

        Returns
        -------
        int
        """

        return self._failures

    def write(self, line):

        """
        Write a JSON object to the output file.

        Parameters
        ----------
        line : See `dumps()` method

        Returns
        -------
        True
            On success.
        False
            If `skip_failures=True` and a failure is encountered.
        """

        try:

            linestring = self.json_lib.dumps(line, **self.kwargs) + self.delimiter
            if not PY3:  # pragma no cover
                linestring = linestring.decode()
            self._f.write(linestring)
            self._line_num += 1

        except Exception as e:
            self._failures += 1
            if not self.skip_failures:
                raise e
            else:
                return False

        # Success
        return True

    # Alias for writer compatibility
    writerow = write