"""
Streaming newline delimited JSON I/O
"""


__version__ = '0.1.0'
__author__ = 'Kevin Wurster'
__email__ = 'wursterk@gmail.com'
__source__ = 'https://github.com/geowurster/NewlineJSON'
__license__ = '''
New BSD License

Copyright (c) 2014, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of its contributors may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


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


JSON = json


# Python 2/3 compatibility
PY3 = sys.version_info[0] is 3
if PY3:  # pragma no cover
    STR_TYPES = (str)
else:  # pragma no cover
    STR_TYPES = (str, unicode)


__all__ = [
    'load', 'loads', 'dump', 'dumps', 'Reader', 'Writer',
]


def load(f, **kwargs):

    """
    Load an entire file of newline delimited JSON into a list where each element
    is a line.  Only use on small files.

    Parameters
    ----------
    f : file
        Open file object from which newline JSON is read.
    kwargs : **kwargs, optional
        Additional keyword arguments for the `Reader()` class.

    Returns
    -------
    list
        One decoded JSON element per line in the input file.
    """

    return [line for line in Reader(f, **kwargs)]


def loads(string, **kwargs):

    """
    Same as `load()` but the input is a string instead of a file object.

    Parameters
    ----------
    kwargs : **kwargs, optional
        Keyword arguments for `Reader.from_string()`
    string : str
        Contains newline delimited JSON

    Returns
    -------
    list
        One decoded JSON element per line in the input string.
    """

    return [line for line in Reader.from_string(string, **kwargs)]


def dump(line_list, f, **kwargs):

    """
    Write a list of JSON objects to an output file one line at a time.

    Parameters
    ----------
    f : file
        Handle to an open writable file object.
    line_list : list, tuple
        A list of JSON objects to be written.
    kwargs : **kwargs, optional
        Additional keyword arguments for the `Writer()` class.

    Returns
    -------
    True
        On success
    """

    writer = Writer(f, **kwargs)
    for line in line_list:
        writer.write(line)

    return True


def dumps(line_list, container=StringIO, **kwargs):

    """
    Same as `dump()` but a string is returned instead of writing each line to
    an output file.

    Parameters
    ----------
    line_list : list, tuple
        A list of JSON objects to be encoded to a string.
    container : StringIO, optional
        File-like object to write to.  Must support `.read()` like `StringIO`
        or `file`.
    kwargs : **kwargs, optional
        Additional keyword arguments for the `Writer()` class.

    Returns
    -------
    str
        Newline delimited JSON string.
    """

    f = container()
    writer = Writer(f, **kwargs)
    for line in line_list:
        writer.write(line)
    f.seek(0)
    return f.read()


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
