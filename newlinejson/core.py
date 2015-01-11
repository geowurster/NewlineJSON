"""
Core functions and classes
"""


import csv
import json
import os
try:
    from io import StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
import sys


# Specify which JSON library to use.  Used everywhere JSON encoding/decoding happens.as
# Allows the user to use ujson, simplejson, yajl, etc. instead of the built in library.
JSON = json


# Figure out if running on Python3
PY3 = sys.version_info[0] == 3


__all__ = [
    'JSON',
    'get_reader', 'get_writer',
    'load', 'loads', 'dump', 'dumps',
    'Reader', 'Writer',
    'DictReader',
    'DictWriter',
    'ListWriter'
]


def get_reader(name):

    """
    Get a reader class by name.  Primarily used by commandline utilities.

    Supported Readers
    -----------------
    csv  --> csv.DictReader
    json --> newlinejson.Reader
    newlinejson --> newlinejson.Reader
    dictwriter  --> newlinejson.DictReader

    Parameters
    ----------
    name : str
        Name of reader as string.

    Returns
    -------
    object

    Raises
    ------
    ValueError
        Unrecognized reader name.
    """

    name = name.lower()
    if name == 'reader':
        return Reader
    elif name == 'dictreader':
        return DictReader
    elif name == 'csv':
        return csv.DictReader
    else:
        raise ValueError("Invalid reader: {name}".format(name=name))


def get_writer(name):

    """
    Get a writer class by name.  Primarily used by commandline utilities.

    Supported Writers
    -----------------
    csv  --> csv.DictWriter
    json --> newlinejson.Writer
    newlinejson --> newlinejson.Writer
    dictwriter  --> newlinejson.DictWriter

    Parameters
    ----------
    name : str
        Name of writer as string.

    Returns
    -------
    object

    Raises
    ------
    ValueError
        Unrecognized writer name.
    """

    name = name.lower()
    if name in ('newlinejson', 'json'):
        return Writer
    elif name == 'csv':
        return csv.DictWriter
    else:
        raise ValueError()


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

    return [i for i in Reader(f, **kwargs)]


def loads(string, **kwargs):

    """
    Same as `load()` but the input is a string instead of a file object.

    Parameters
    ----------
    string : str
        Formatted string to be parsed
    kwargs : **kwargs, optional
        Additional keyword arguments for the `Reader()` class.

    Returns
    -------
    list
        One decoded JSON element per line in the input string.
    """

    if not PY3:
        string = string.decode()

    with StringIO(string) as f:
        return load(f, **kwargs)


def dump(line_list, f, **kwargs):

    """
    Write a list of JSON objects to an output file one line at a time.

    Parameters
    ----------
    line_list : list, tuple
        A list of JSON objects to be written.
    f : file
        Handle to an open writable file object.
    kwargs : **kwargs, optional
        Additional keyword arguments for the `Writer()` class.

    Returns
    -------
    True
        On success
    """

    if not isinstance(line_list, (list, tuple)):
        raise TypeError("Input JSON objects must be in a list or tuple")

    writer = Writer(f, **kwargs)
    for line in line_list:
        writer.write(line)

    return True


def dumps(line_list, **kwargs):

    """
    Same as `dump()` but a string is returned instead of writing each line to
    an output file.

    Parameters
    ----------
    line_list : list, tuple
        A list of JSON objects to be encoded to a string.
    kwargs : **kwargs, optional
        Additional keyword arguments for the `Writer()` class.

    Returns
    -------
    str
        Newline delimited JSON string.
    """

    if not isinstance(line_list, (list, tuple)):
        raise TypeError("Input JSON objects must be in a list or tuple")

    with StringIO() as f:
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
                 *args, **kwargs):

        """
        Read a file containing newline delimited JSON.

        Parameters
        ---------
        f : file
            Handle to an open file object that is open for reading.
        skip_lines : int, optional
            Number of lines to immediately skip.
        skip_failures : bool, optional
            If True, exceptions thrown by `newlinejson.JSON.loads()` will be
            suppressed and the offending line will be ignored.
        skip_empty : bool, optional
            If True, skip empty lines.
        fail_val : anything, optional
            Value to return if `skip_failures=True` and a line cannot be decoded.
        empty_val : anything, optional
            Value to return if `skip_empty=False` - since an empty line has no
            corresponding JSON object, something must be returned.
        args : *args, optional
            Eats additional positional arguments so this class can be
            transparently swapped with other readers.
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.JSON.loads()`.
        """

        self._f = f
        self.skip_lines = skip_lines
        self.skip_failures = skip_failures
        self.skip_empty = skip_empty
        self.line_num = 0
        self.fail_val = fail_val
        self.empty_val = empty_val
        self.kwargs = kwargs

        for i in range(skip_lines):
            self.next()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def _readline(self):

        """
        Handle Python3 `__next__()` vs. `next()`.

        Returns
        -------
        str
            The next stripped line from the file.
        """

        self.line_num += 1

        try:
            return self._f.__next__().strip()
        except AttributeError:
            return self._f.next().strip()

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
            elif row == '':
                return self.empty_val

            return JSON.loads(row, **self.kwargs)

        except ValueError as e:

            if not self.skip_failures:
                raise e
            else:
                return self.fail_val


class Writer(object):

    """
    Write newline delimited JSON.
    """

    def __init__(self, f, skip_failures=False, delimiter=os.linesep, *args, **kwargs):

        """
        Read a file containing newline delimited JSON.

        Parameters
        ---------
        f : file
            Handle to an open writable file-like object.
        skip_failures : bool, optional
            If True, exceptions thrown by `newlinejson.JSON.dumps()` will be
            suppressed and the offending line will be ignored.
        delimiter : str, optional
            Newline character to be written after every row.
        args : *args, optional
            Eats additional positional arguments so this class can be
            transparently swapped with other writers.
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.JSON.dumps()`.
        """

        self._f = f
        self.skip_failures = skip_failures
        self.delimiter = delimiter
        self.kwargs = kwargs

    def write(self, line):

        """
        Write a JSON object to the output file.

        Parameters
        ----------
        line : dict, list, or tuple
            Anything `newlinejson.JSON.dumps()` can serialize to a string

        Returns
        -------
        True
            On success
        False
            If `skip_failures=True`
        """

        try:

            # The built-in `json.dumps()` decodes to `str` so if it fails, try calling the `decode()`
            # method to force unicode.  Other readers could exhibit similar problems.
            try:
                self._f.write(JSON.dumps(line, **self.kwargs) + self.delimiter)
            except Exception:
                self._f.write(JSON.dumps(line, **self.kwargs).decode() + self.delimiter)

            return True

        except Exception as e:
            if not self.skip_failures:
                raise e
            else:
                return False


class DictReader(object):

    """
    Read newline JSON as a dictionary.
    """

    def __init__(self, f, fieldnames=None, skip_lines=0, skip_failures=False, restkey=None, restval=None, reader=Reader,
                 *args, **kwargs):

        """
        Read newline JSON like `csv.DictReader()`.

        If the input file contains both lists/tuples and dictionaries then the
        `fieldnames` option must specify the fields in the order they appear in
        the list/tuple rows.  The dictionaries are automatically taken care of.

        The `reader` option allows the user to specify the reader best suited
        to the input file object, has only a few requirements, and allows the
        user to develop their own reader for specific use-cases while still
        taking advantage of the parsing and validation offered by this class.

        Parameters
        ----------
        f : file
            Input file object open for reading
        fieldnames : list or tuple, optional
            Fieldnames to read.  If `None` and the first row is a list, it is
            used.  If the first row is a dictionary, its keys are used.
        restkey : str, optional
            If an input row contains more fields than `fieldnames` the extras
            will be moved to `restkey's` value
        restval : str, optional
            If an input row contains fewer fields than `fieldnames` the
            additional `fieldnames` are added with their val set to `restval`
        reader : object, optional
            Class to use for reading `f`.  This can be anything as long as the
            first positional argument is a file-like object, it accepts
            `*args/**kwargs`, and `reader.next()` returns a valid JSON object.
        args : *args
            Additional positional arguments for `reader`
        kwargs : **kwargs
            Additional keyword arguments for `reader`
        """

        self.reader = reader(f, *args, **kwargs)
        self.restkey = restkey
        self.restval = restval
        self._first_row = None
        self.skip_failures = skip_failures
        if self.fieldnames is not None:
            self.fieldnames = list(fieldnames)
        if self.fieldnames is None:
            self._first_row = self.reader.next()
            self.fieldnames = self._first_row.keys()
        for _i in range(skip_lines):
            self.next()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    @property
    def line_num(self):

        """
        Get the current line number.

        Returns
        -------
        int
        """

        return self.reader.line_num

    def next(self):

        """
        Get the next JSON object from the reader and handle `restkey`, `restval`,
        and differences in control flow for when rows are `list` or `dict`.

        Returns
        -------
        dict, list, tuple
            Whatever is returned by `newlinejson.JSON.dumps()`
        """

        # If the first row is cached then that means the first row of the input file is being used as the header
        # (or if its a dict, its keys), which means this row is properly formatted and contains valid fields
        if self._first_row is not None:
            output = self._first_row
            self._first_row = None
            return output

        # == Based on csv.DictReader.next() == #
        row = self.reader.next()

        # Convert list rows to dictionaries
        if isinstance(row, (list, tuple)):
            output = zip(self.fieldnames, row)
        else:
            output = row

        len_fieldnames = len(self.fieldnames)
        len_row = len(output)

        # Handle restkey
        if len_fieldnames < len_row:
            output[self.restkey] = {k: v for k, v in row if k not in self.fieldnames}

        # Handle restval
        elif len_fieldnames > len_row:
            for key in self.fieldnames[len_fieldnames:]:
                output[key] = self.restval

        return row


class DictWriter(object):

    """
    Write dictionaries to newline JSON.
    """

    def __init__(self, f, fieldnames, restval=None, extrasaction='raise', writer=Writer,
                 *args, **kwargs):

        """
        Write dictionaries to newline JSON like `csv.DictWriter()`.

        Parameters
        ----------
        f : file
            Input file object open for writing.
        fieldnames : list or tuple
            Fieldnames to be written.
        restval : object, optional
            If `extrasaction` is 'ignore' and some fields in `fieldnames` are not
            present in a row being written, `restval` is assigned to the fields.
            Can be anything serializable by `newlinejson.JSON.dumps()`.
        extrasaction : str, optional
            Describes what to do if a row being written has fields that are not
            present in `fieldnames`.  If set to 'raise' a `ValueError` will be
            raised.  If set to 'ignore' the additional content will be written.
        writer : object, optional
            Class to use for writing to `f`.  This can be anything as long as
            the first positional argument is a file-like object, the second is
            a list of fieldnames to write, it accepts `*args/**kwargs`, and has a
            `write()` method that accepts a dictionary.
        args : *args
            Additional positional arguments for `writer`
        kwargs : **kwargs
            Additional keyword arguments for `writer`
        """

        self.writer = writer(f, *args, **kwargs)
        self.restval = restval
        self.fieldnames = list(fieldnames)
        self.extrasaction = extrasaction.lower()
        _extrasactions = ('raise', 'ignore')
        if self.extrasaction is not None and self.extrasaction not in _extrasactions:
            raise ValueError("Invalid extrasaction ({ea}) - must be: {eo}".format(
                ea=self.extrasaction, eo=', '.join(_extrasactions)))

    def writeheader(self):

        """
        Does nothing.  Included for transparency
        """

        pass

    def writerow(self, row):

        """
        Encode a JSON object and write it via the `writer`.

        Parameters
        ----------
        row : dict, list, tuple
            An object serializable by `newlinejson.JSON.dumps()`
        """

        if self.extrasaction == "raise":
            wrong_fields = [repr(k) for k in row if k not in self.fieldnames]
            if wrong_fields:
                raise ValueError("Row contains fields not in fieldnames: {fields}".format(', '.join(wrong_fields)))

        return self.writer.write({k: row.get(k, self.restval) for k in self.fieldnames})

    # Alias
    write = writerow

    def writerows(self, rows):

        """
        Write multiple rows to the output file.

        Parameters
        ----------
        rows : list
            List of JSON objects to write.

        Returns
        -------
        True
            On success.
        """

        for row in rows:
            self.writerow(row)

        return True


class ListWriter(object):

    """
    Like `DictWriter()` but writes lists
    """

    def __init__(self, f, fieldnames, restval=None, extrasaction='raise', writer=Writer,
                 *args, **kwargs):

        """
        Write dictionaries to newline JSON with a more CSV-like structure.

        Input example:

            {"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}
            {"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"}
            {"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"}
            {"field2": "l4f2", "field3": "l4f3", "field1": "l4f1"}
            {"field2": "l5f2", "field3": "l5f3", "field1": "l5f1"}

        Output example:

            ["field1", "field2", "field3"]
            ["l1f1", "l1f2", "l1f3"]
            ["l2f1", "l2f2", "l3f3"]
            ["l3f1", "l3f2", "l3f3"]
            ["l4f1", "l4f2", "l4f3"]
            ["l5f1", "l5f2", "l5f3"]

        Parameters
        ----------
        f : file
            Input file object open for writing.
        fieldnames : list or tuple
            Fieldnames to be written.
        restval : object, optional
            If `extrasaction` is 'ignore' and some fields in `fieldnames` are not
            present in a row being written, `restval` is assigned to the fields.
            Can be anything serializable by `newlinejson.JSON.dumps()`.
        extrasaction : str, optional
            Describes what to do if a row being written has fields that are not
            present in `fieldnames`.  If set to 'raise' a `ValueError` will be
            raised.  If set to 'ignore' the additional content will be written.
        writer : object, optional
            Class to use for writing to `f`.  This can be anything as long as
            the first positional argument is a file-like object, the second is
            a list of fieldnames to write, it accepts `*args/**kwargs`, and has a
            `write()` method that accepts a dictionary.
        args : *args
            Additional positional arguments for `writer`
        kwargs : **kwargs
            Additional keyword arguments for `writer`
        """

        self.writer = writer(f, *args, **kwargs)
        self.restval = restval
        self.fieldnames = list(fieldnames)
        self.extrasaction = extrasaction.lower()
        _extrasactions = ('raise', 'ignore')
        if self.extrasaction is not None and self.extrasaction not in _extrasactions:
            raise ValueError("Invalid extrasaction ({ea}) - must be: {eo}".format(
                ea=self.extrasaction, eo=', '.join(_extrasactions)))

    def writeheader(self):

        """
        Write a header row to the output file.

        Returns
        -------
        object
            Output from `writer.write()`
        """

        return self.writer.write(self.fieldnames)

    def writerow(self, row):

        """
        Encode a JSON object and write it via the `writer`.

        Parameters
        ----------
        row : dict, list, tuple
            An object serializable by `newlinejson.JSON.dumps()`
        """

        if self.extrasaction == "raise":
            wrong_fields = [repr(k) for k in row if k not in self.fieldnames]
            if wrong_fields:
                raise ValueError("Row contains fields not in fieldnames: {fields}".format(', '.join(wrong_fields)))

        return self.writer.write([row.get(k, self.restval) for k in self.fieldnames])

    # Alias
    write = writerow

    def writerows(self, rows):

        """
        Write multiple rows to the output file.

        Parameters
        ----------
        rows : list
            List of JSON objects to write.

        Returns
        -------
        True
            On success.
        """

        for row in rows:
            self.writerow(row)

        return True
