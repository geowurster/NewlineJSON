"""
Core functions and classes
"""


import csv
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
PY3 = sys.version_info[0] == 3
if PY3:  # pragma no cover
    STR_TYPES = (str)
else:  # pragma no cover
    STR_TYPES = (str, unicode)


__all__ = [
    'PY3',
    'get_reader', 'get_writer',
    'load', 'loads', 'dump', 'dumps',
    'Reader', 'Writer',
]


def get_reader(name):

    """
    Get a reader class by name.  Primarily used by commandline utilities.

    Supported Readers
    -----------------
    csv  --> csv.DictReader
    json --> newlinejson.Reader
    newlinejson --> newlinejson.Reader

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
    if name == 'newlinejson':
        return Reader
    elif name == 'json':
        return Reader
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
    if name in 'newlinejson':
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

    return [line for line in Reader(f, **kwargs)]


def loads(string, **kwargs):

    """
    Same as `load()` but the input is a string instead of a file object.

    Parameters
    ----------
    string : str
        Contains newline delimited JSON
    kwargs : **kwargs, optional
        Keyword arguments for `Reader.from_string()`

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
        f : file
            Handle to an open file object that is open for reading.
        skip_lines : int, optional
            Number of lines to immediately skip with `next(f)`
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
        json_lib : module, optional
            Specify which JSON library to use for this instance
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.JSON.loads()`.

        Attributes
        ----------
        f : file
            Handle to the input file.
        skip_lines : int
            Number of lines that were skipped on instantiation.
        skip_failures : bool
            Are failures being skipped?
        skip_empty : bool
            Are empty lines being skipped?
        line_num : int
            Line number that was most recently read.
        fail_val : anything
            Value being returned from `next()` when a failure is encountered.
        kwargs : dict
            Keyword args being passed to `self.json_lib.loads()`
        json_lib : module
            JSON library currently being used for decoding
        """

        self._f = f
        self.skip_lines = skip_lines
        self.skip_failures = skip_failures
        self.skip_empty = skip_empty
        self._line_num = 0
        self.fail_val = fail_val
        self.empty_val = empty_val
        self.kwargs = kwargs
        if json_lib is None:
            self.json_lib = JSON
        else:
            self.json_lib = json_lib

        for i in range(skip_lines):
            self._line_num += 1
            next(self._f)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

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
    def line_num(self):

        """
        Line number of the previous line that was read.

        Returns
        -------
        int
        """

        return self._line_num

    @classmethod
    def from_string(cls, string, container=StringIO, **kwargs):

        """
        Create a `Reader()` instance with a string containing newline delimited
        JSON instead of a file-like object.

        Parameters
        ----------
        string : str
            Contains newline delimited JSON
        container : StringIO, optional
            Class used to convert a string to a file-like object.
        kwargs : **kwargs, optional
            Keyword arguments for `Reader()`

        Returns
        -------
        Reader
        """

        if not PY3:  # pragma no cover
            string = string.decode()

        return cls(container(string), **kwargs)

    # def seek(self, target_line):
    #
    #     """
    #     Move the cursor to the beginning of the specified line, which is zero
    #     indexing.  `seek_line(1)` means the next line read will be the second
    #     line in the file.
    #
    #     Parameters
    #     ----------
    #     target_line : int
    #         Move the cursor to this index.
    #
    #     Returns
    #     -------
    #     True
    #         On success
    #
    #     Notes
    #     -----
    #     - The input file-like object must support `seek(0)` in order to initially
    #     move the cursor to the very beginning of the file.
    #     - Each line in the input file is iterated over until the desired position
    #     is found so this method will not work when streaming from `sys.stdin` and
    #     will be inefficient when working with large files.
    #     - Instead of decoding every line to JSON while seeking only the input
    #     file-like object is iterated over.
    #     """
    #
    #     # Must manually the line counter but ONLY if we successfully move the cursor to the beginning of the input
    #     # file-like object, otherwise the line counter could be reset and not accurately reflect the current position.
    #     self._f.seek(0)
    #     self._line_num = 0
    #     while target_line <= self._line_num:
    #         try:
    #             next(self._f)
    #             self._line_num += 1
    #         except StopIteration:
    #             break
    #
    #     return True

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

            if not self.skip_failures:
                raise e
            else:
                return self.fail_val


class Writer(object):

    """
    Write newline delimited JSON.
    """

    def __init__(self, f, skip_failures=False, delimiter=os.linesep, json_lib=JSON, **kwargs):

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
        kwargs : **kwargs, optional
            Additional keyword arguments for `newlinejson.JSON.dumps()`.

        Attributes
        ----------
        f : file
            Handle to the input file.
        skip_failures : bool
            Are failures being skipped?
        delimiter : str
            Newline character
        kwargs : dict
            Keyword args being passed to `self.json_lib.dumps()`
        line_num : int
            Line number that was most recently written.
        json_lib : module
            JSON library currently being used for decoding
        """

        self._f = f
        self.skip_failures = skip_failures
        self.delimiter = delimiter
        self.kwargs = kwargs
        self._line_num = 0
        self.json_lib = json_lib

    @property
    def line_num(self):

        """
        Index to the line that was just written.  Index 0 is line 1, just like
        a list.  Only successfully written lines are recorded.

        Returns
        -------
        int
        """

        return self._line_num

    @property
    def f(self):

        """
        Handle to the file-like object from which lines are being read.

        Returns
        -------
        file
        """

        return self._f

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
            if not PY3:
                linestring = linestring.decode()
            self._f.write(linestring)
            self._line_num += 1

        except Exception as e:
            if not self.skip_failures:
                raise e
            else:
                return False

        # Success
        return True

    # Alias for writer compatibility
    writerow = write


# class DictWriter(Writer):
#
#     def __init__(self, f, fieldnames, allow_extra=False, extra_val=None, *args, **kwargs):
#
#         Writer.__init__(self, f, *args, **kwargs)
#
#         self.fieldnames = fieldnames
#         self.skip_failures = kwargs.get('skip_failures', False)
#         self.allow_extra = allow_extra
#         self.extra_val = extra_val
#
#         self._sorted_fieldnames = sorted(fieldnames)
#
#     def writeheader(self):
#
#         pass
#
#     def _format_output(self, line):
#
#         if isinstance(line, dict):
#             if not self.allow_extra and sorted(line.keys()) != self._sorted_fieldnames:
#                 raise ValueError("Dict line has undeclared fields: fieldnames='{fieldnames}' line='{line}'".format(
#                     fieldnames=self.fieldnames, line=line))
#             else:
#                 return {field: line.get(field, self.extra_val) for field in self.fieldnames}
#         else:
#             if not self.allow_extra and len(line) is not len(self.fieldnames):
#                 raise ValueError("List line has too many or too few values: fieldnames='{fieldnames}' line='{line}'"
#                                  .format(fieldnames=self.fieldnames, line=line))
#             else:
#                 _line_filler = [self.extra_val] * len(self.fieldnames) - len(line)
#                 return {field: value for field, value in zip(self.fieldnames, line + _line_filler)}
#
#     def write(self, line):
#
#         try:
#             return Writer.write(self, self._format_output(line))
#         except Exception as e:
#             if not self.skip_failures:
#                 raise e
#
#     writerow = write
#

# class ListWriter(Writer, DictWriter):
#
#     def __init__(self, f, fieldnames, *args, **kwargs):
#
#         Writer.__init__(f, *args, **kwargs)
#         DictWriter.__init__(f, fieldnames, *args, **kwargs)
#
#         self.skip_failures = kwargs.get('skip_failures', False)
#
#     def writeheader(self):
#         pass
#
#     def write(self, line):
#         try:
#             pass
#         except Exception as e:
#             if not self.skip_failures:
#                 raise e
#
#     writerow = write
#
#
# class CsvDictReader(object):
#
#     """
#     Read newline JSON as a dictionary.
#     """
#
#     def __init__(self, f, fieldnames=None, skip_lines=0, skip_failures=False, restkey=None, restval=None, reader=Reader,
#                  *args, **kwargs):
#
#         """
#         Read newline JSON like `csv.DictReader()`.
#
#         If the input file contains both lists/tuples and dictionaries then the
#         `fieldnames` option must specify the fields in the order they appear in
#         the list/tuple rows.  The dictionaries are automatically taken care of.
#
#         The `reader` option allows the user to specify the reader best suited
#         to the input file object, has only a few requirements, and allows the
#         user to develop their own reader for specific use-cases while still
#         taking advantage of the parsing and validation offered by this class.
#
#         Parameters
#         ----------
#         f : file
#             Input file object open for reading
#         fieldnames : list or tuple, optional
#             Fieldnames to read.  If `None` and the first row is a list, it is
#             used.  If the first row is a dictionary, its keys are used.
#         restkey : str, optional
#             If an input row contains more fields than `fieldnames` the extras
#             will be moved to `restkey's` value
#         restval : str, optional
#             If an input row contains fewer fields than `fieldnames` the
#             additional `fieldnames` are added with their val set to `restval`
#         reader : object, optional
#             Class to use for reading `f`.  This can be anything as long as the
#             first positional argument is a file-like object, it accepts
#             `*args/**kwargs`, and `reader.next()` returns a valid JSON object.
#         args : *args
#             Additional positional arguments for `reader`
#         kwargs : **kwargs
#             Additional keyword arguments for `reader`
#         """
#
#         self.reader = reader(f, *args, **kwargs)
#         self.restkey = restkey
#         self.restval = restval
#         self._first_row = None
#         self.skip_failures = skip_failures
#         if self.fieldnames is not None:
#             self.fieldnames = list(fieldnames)
#         if self.fieldnames is None:
#             self._first_row = self.reader.next()
#             self.fieldnames = self._first_row.keys()
#         for _i in range(skip_lines):
#             self.next()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         return self.next()
#
#     @property
#     def line_num(self):
#
#         """
#         Get the current line number.
#
#         Returns
#         -------
#         int
#         """
#
#         return self.reader.line_num
#
#     def next(self):
#
#         """
#         Get the next JSON object from the reader and handle `restkey`, `restval`,
#         and differences in control flow for when rows are `list` or `dict`.
#
#         Returns
#         -------
#         dict, list, tuple
#             Whatever is returned by `newlinejson.JSON.dumps()`
#         """
#
#         # If the first row is cached then that means the first row of the input file is being used as the header
#         # (or if its a dict, its keys), which means this row is properly formatted and contains valid fields
#         if self._first_row is not None:
#             output = self._first_row
#             self._first_row = None
#             return output
#
#         # == Based on csv.DictReader.next() == #
#         row = self.reader.next()
#
#         # Convert list rows to dictionaries
#         if isinstance(row, (list, tuple)):
#             output = zip(self.fieldnames, row)
#         else:
#             output = row
#
#         len_fieldnames = len(self.fieldnames)
#         len_row = len(output)
#
#         # Handle restkey
#         if len_fieldnames < len_row:
#             output[self.restkey] = {k: v for k, v in row if k not in self.fieldnames}
#
#         # Handle restval
#         elif len_fieldnames > len_row:
#             for key in self.fieldnames[len_fieldnames:]:
#                 output[key] = self.restval
#
#         return row
#
#
# class CsvDictWriter(object):
#
#     """
#     Write dictionaries to newline JSON.
#     """
#
#     def __init__(self, f, fieldnames, restval=None, extrasaction='raise', writer=Writer,
#                  *args, **kwargs):
#
#         """
#         Write dictionaries to newline JSON like `csv.DictWriter()`.
#
#         Parameters
#         ----------
#         f : file
#             Input file object open for writing.
#         fieldnames : list or tuple
#             Fieldnames to be written.
#         restval : object, optional
#             If `extrasaction` is 'ignore' and some fields in `fieldnames` are not
#             present in a row being written, `restval` is assigned to the fields.
#             Can be anything serializable by `newlinejson.JSON.dumps()`.
#         extrasaction : str, optional
#             Describes what to do if a row being written has fields that are not
#             present in `fieldnames`.  If set to 'raise' a `ValueError` will be
#             raised.  If set to 'ignore' the additional content will be written.
#         writer : object, optional
#             Class to use for writing to `f`.  This can be anything as long as
#             the first positional argument is a file-like object, the second is
#             a list of fieldnames to write, it accepts `*args/**kwargs`, and has a
#             `write()` method that accepts a dictionary.
#         args : *args
#             Additional positional arguments for `writer`
#         kwargs : **kwargs
#             Additional keyword arguments for `writer`
#         """
#
#         self.writer = writer(f, *args, **kwargs)
#         self.restval = restval
#         self.fieldnames = list(fieldnames)
#         self.extrasaction = extrasaction.lower()
#         _extrasactions = ('raise', 'ignore')
#         if self.extrasaction is not None and self.extrasaction not in _extrasactions:
#             raise ValueError("Invalid extrasaction ({ea}) - must be: {eo}".format(
#                 ea=self.extrasaction, eo=', '.join(_extrasactions)))
#
#     def writeheader(self):
#
#         """
#         Does nothing.  Included for transparency
#         """
#
#         pass
#
#     def writerow(self, row):
#
#         """
#         Encode a JSON object and write it via the `writer`.
#
#         Parameters
#         ----------
#         row : dict, list, tuple
#             An object serializable by `newlinejson.JSON.dumps()`
#         """
#
#         if self.extrasaction == "raise":
#             wrong_fields = [repr(k) for k in row if k not in self.fieldnames]
#             if wrong_fields:
#                 raise ValueError("Row contains fields not in fieldnames: {fields}".format(', '.join(wrong_fields)))
#
#         return self.writer.write({k: row.get(k, self.restval) for k in self.fieldnames})
#
#     # Alias
#     write = writerow
#
#     def writerows(self, rows):
#
#         """
#         Write multiple rows to the output file.
#
#         Parameters
#         ----------
#         rows : list
#             List of JSON objects to write.
#
#         Returns
#         -------
#         True
#             On success.
#         """
#
#         for row in rows:
#             self.writerow(row)
#
#         return True
#
#
# class ListWriter(object):
#
#     """
#     Like `DictWriter()` but writes lists
#     """
#
#     def __init__(self, f, fieldnames, restval=None, extrasaction='raise', writer=Writer,
#                  *args, **kwargs):
#
#         """
#         Write dictionaries to newline JSON with a more CSV-like structure.
#
#         Input example:
#
#             {"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}
#             {"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"}
#             {"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"}
#             {"field2": "l4f2", "field3": "l4f3", "field1": "l4f1"}
#             {"field2": "l5f2", "field3": "l5f3", "field1": "l5f1"}
#
#         Output example:
#
#             ["field1", "field2", "field3"]
#             ["l1f1", "l1f2", "l1f3"]
#             ["l2f1", "l2f2", "l3f3"]
#             ["l3f1", "l3f2", "l3f3"]
#             ["l4f1", "l4f2", "l4f3"]
#             ["l5f1", "l5f2", "l5f3"]
#
#         Parameters
#         ----------
#         f : file
#             Input file object open for writing.
#         fieldnames : list or tuple
#             Fieldnames to be written.
#         restval : object, optional
#             If `extrasaction` is 'ignore' and some fields in `fieldnames` are not
#             present in a row being written, `restval` is assigned to the fields.
#             Can be anything serializable by `newlinejson.JSON.dumps()`.
#         extrasaction : str, optional
#             Describes what to do if a row being written has fields that are not
#             present in `fieldnames`.  If set to 'raise' a `ValueError` will be
#             raised.  If set to 'ignore' the additional content will be written.
#         writer : object, optional
#             Class to use for writing to `f`.  This can be anything as long as
#             the first positional argument is a file-like object, the second is
#             a list of fieldnames to write, it accepts `*args/**kwargs`, and has a
#             `write()` method that accepts a dictionary.
#         args : *args
#             Additional positional arguments for `writer`
#         kwargs : **kwargs
#             Additional keyword arguments for `writer`
#         """
#
#         self.writer = writer(f, *args, **kwargs)
#         self.restval = restval
#         self.fieldnames = list(fieldnames)
#         self.extrasaction = extrasaction.lower()
#         _extrasactions = ('raise', 'ignore')
#         if self.extrasaction is not None and self.extrasaction not in _extrasactions:
#             raise ValueError("Invalid extrasaction ({ea}) - must be: {eo}".format(
#                 ea=self.extrasaction, eo=', '.join(_extrasactions)))
#
#     def writeheader(self):
#
#         """
#         Write a header row to the output file.
#
#         Returns
#         -------
#         object
#             Output from `writer.write()`
#         """
#
#         return self.writer.write(self.fieldnames)
#
#     def writerow(self, row):
#
#         """
#         Encode a JSON object and write it via the `writer`.
#
#         Parameters
#         ----------
#         row : dict, list, tuple
#             An object serializable by `newlinejson.JSON.dumps()`
#         """
#
#         if self.extrasaction == "raise":
#             wrong_fields = [repr(k) for k in row if k not in self.fieldnames]
#             if wrong_fields:
#                 raise ValueError("Row contains fields not in fieldnames: {fields}".format(', '.join(wrong_fields)))
#
#         return self.writer.write([row.get(k, self.restval) for k in self.fieldnames])
#
#     # Alias
#     write = writerow
#
#     def writerows(self, rows):
#
#         """
#         Write multiple rows to the output file.
#
#         Parameters
#         ----------
#         rows : list
#             List of JSON objects to write.
#
#         Returns
#         -------
#         True
#             On success.
#         """
#
#         for row in rows:
#             self.writerow(row)
#
#         return True
