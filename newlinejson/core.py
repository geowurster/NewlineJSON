"""
Core functions and classes
"""


import os

import json


# Specify which JSON library to use
JSON = json


__all__ = ['JSON', 'Reader', 'Writer']


class Reader(object):

    """
    Read newline delimited JSON objects
    """

    def __init__(self, f, skiplines=0, skip_failures=False, skip_empty=False, *args, **kwargs):

        """
        Read a file containing newline delimited JSON.

        Parameters
        ---------
        f : file
            Handle to an open file object that is open for reading
        skiplines : int, optional
            Number of lines to immediately skip
        skip_failures : bool, optional
            If True, exceptions thrown by `json.loads()` will be suppressed and
            the offending line will be ignored
        skip_empty : bool, optional
            If True, skip empty lines
        args : *args, optional
            Eats additional positional arguments so the reader can be
            transparently swapped with other readers
        kwargs : **kwargs, optional
            Eats additional keyword arguments so the reader can be transparently
            swapped with other readers
        """

        self._f = f
        self.skiplines = skiplines
        self.skip_failures = skip_failures
        self.skip_empty = skip_empty
        self.line_num = 0

        for i in range(skiplines):
            self.next()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

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

            row = self._f.readline()
            if self.skip_empty:
                while not row:
                    row = self._f.readline()

            self.line_num += 1
            return JSON.loads(row)

        except ValueError as e:

            if not self.skip_failures:
                raise e


class Writer(object):

    """
    Write newline delimited JSON objects
    """

    def __init__(self, f, skip_failures=False, delimiter=os.linesep, *args, **kwargs):

        """
        Read a file containing newline delimited JSON.

        Parameters
        ---------
        f : file
            Handle to an open file object that is open for writing
        skip_failures : bool, optional
            If True, exceptions thrown by `json.dumps()` will be suppressed
            and the offending line will be ignored
        args : *args
            Eats additional positional arguments so the reader can be
            transparently swapped with other readers
        kwargs : **kwargs
            Eats additional keyword arguments so the reader can be transparently
            swapped with other readers
        """

        self._f = f
        self.skip_failures = skip_failures
        self.delimiter = delimiter

    def writerow(self, line):

        """
        Write a JSON object to the output file.

        Parameters
        ----------
        line : dict or list
            Keys, values, and elements must be an object `json.dumps()` can
            serialize

        Returns
        -------
        True
            On success
        """

        try:
            self._f.write(JSON.dumps(line) + self.delimiter)
        except Exception as e:
            if not self.skip_failures:
                raise e

        return True
#
#
# class DictReader(object):
#
#     """
#     Read newline delimited JSON like `csv.DictReader()`
#     """
#
#     def __init__(self, f, fieldnames=None, restkey=None, restval=None, *args, **kwargs):
#
#         """
#         Newline delimited JSON that is hot-swappable with `csv.DictReader`.
#
#         The input rows are expected to be lists of the same length or
#         dictionaries containing the same keys.  If `fieldnames` are supplied
#         then only specific fields will be read.
#
#         Examples:
#
#             >>> from StringIO import StringIO
#             >>>
#             >>> # Lists with header
#             >>> f = StringIO('["field1","field2","field3"]' + \
#                              '["l1f1","l1f2","l1f3"]' + \
#                              '["l2f1","l2f2","l3f3"]' + \
#                              '["l3f1","l3f2","l3f3"]')
#             >>> reader = DictReader(f)
#             >>> print(reader.next())
#             {'field1': 'l1f1', 'field2': 'l1f2', 'field3': 'l1f3'}
#             >>>
#             >>> # Same as above but assign new column names
#             >>> reader = DictReader(f, fieldnames=['f1', 'f2', 'f3'], skiplines=1)
#             >>> print(reader.next())
#             {'f1': 'l1f1', 'f2': 'l1f2', 'f3': 'l1f3'}
#             >>>
#             >>> # Lists without header
#             >>> f = StringIO('["l1f1","l1f2","l1f3"]' + \
#                              '["l2f1","l2f2","l3f3"]' + \
#                              '["l3f1","l3f2","l3f3"]')
#             >>> reader = DictReader(f, fieldnames=["field1", "field2", "field3"])
#             >>> print(reader.next())
#             {'field1': 'l1f1', 'field2': 'l1f2', 'field3': 'l1f3'}
#             >>>
#             >>> # Dictionaries
#             >>> f = StringIO('{"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}' + \
#                              '{"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"}' + \
#                              '{"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"}')
#             >>> reader = DictReader(f)
#             >>> print(reader.next())
#             {"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}
#
#         Parameters
#         ----------
#         f : file
#             Handle to a file object that is open for reading
#         fieldnames : list or None, optional
#             Fieldnames to read - if `None` then the fieldnames are pulled
#             from the first line
#         args : *args
#             Positional arguments for `Reader()`
#         kwargs : **kwargs
#             Keyword arguments for `Reader()`
#         """
#
#         self.reader = Reader(f, *args, **kwargs)
#         self._fieldnames = list(fieldnames)
#
#         self.restkey = restkey
#         self.restval = restval
#
#     def __iter__(self):
#         return self
#
#     @property
#     def fieldnames(self):
#
#         """
#         Return the fieldnames being read
#
#         Returns
#         -------
#         list
#         """
#
#         return self._fieldnames
#
#     def next(self):
#
#         """
#         Read and decode the next non-blank line.  See `Reader.next()` for more
#         information.
#
#         Returns
#         -------
#         dict
#         """
#
#         try:
#
#             # Get the next non-empty row
#             row = self.reader.next()
#             while not row:
#                 row = self.reader.next()
#
#             if isinstance(row, list):
#                 output = dict(zip(self.fieldnames, row))
#             else:
#                 output = row
#
#             # From csv.DictReader.next()
#             num_fieldnames = len(self.fieldnames)
#             num_row_keys = len(row)
#             if num_fieldnames < num_row_keys:
#                 output[self.restkey] = row[num_fieldnames:]
#             elif num_fieldnames > num_row_keys:
#                 for key in self.fieldnames[num_row_keys]:
#                     output[key] = self.restval
#
#             return output
#
#         except Exception as e:
#             if not self.reader.skip_failures:
#                 raise e
#
#
# class DictWriter(object):
#
#     """
#     Write newline delimited JSON like `csv.DictWriter()`
#     """
#
#     def __init__(self, f, fieldnames=None, restval=None, *args, **kwargs):
#
#         """
#         Encode and write dictionaries to an output file.
#
#         Each dictionary is written one line at a time and a delimiter
#         is added at the end of the line.
#
#         Output file example:
#
#             '{"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}'
#             '{"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"}'
#             '{"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"}'
#
#         Parameters
#         ----------
#         f : file
#             Handle to an open file object that is open for writing
#         skip_failures : bool, optional
#             If True, exceptions thrown by `json.dumps()` will be suppressed
#             and the offending line will be ignored
#         fieldnames : list, optional
#             Fieldnames to write
#         args : *args
#             Positional arguments for `Writer()`
#         kwargs : **kwargs
#             Keyword arguments for `Writer()`
#         """
#
#         self._fieldnames = list(fieldnames)
#         self.writer = Writer(f, *args, **kwargs)
#
#     @property
#     def fieldnames(self):
#
#         """
#         Return the fieldnames being written
#
#         Returns
#         -------
#         list
#         """
#
#         return self._fieldnames
#
#     def writeheader(self):
#
#         """
#         Since each line is a dictionary this method does nothing but it is
#         included to allow for the writer to be transparently swapped with
#         `csv.DictWriter()`
#         """
#
#         pass
#
#     def writerow(self, row):
#
#         """
#         Write a dictionary to the output file.
#
#         Parameters
#         ----------
#         row : dict
#         """
#
#
#
#
#
#
# class ListWriter(object):
#
#     """
#     Write newline delimited JSON like `csv.DictWriter()`
#     """
#
#     def __init__(self, f, fieldnames, restval=None, *args, **kwargs):
#
#         """
#         Encode and write a list's values to an output file.
#
#         Each dictionary is written one line at a time and a delimiter
#         is added at the end of the line.  A header can be written if
#         the `writeheader()` method is called first.
#
#         Parameters
#         ----------
#         f : file
#             Handle to an open file object that is open for writing
#         skip_failures : bool, optional
#             If True, exceptions thrown by `json.dumps()` will be suppressed
#             and the offending line will be ignored
#         fieldnames : list, optional
#             Fieldnames to write
#         args : *args
#             Positional arguments for `Writer()`
#         kwargs : **kwargs
#             Keyword arguments for `Writer()`
#         """
#
#         self.writer = Writer(f, *args, **kwargs)
#
#         self._fieldnames = list(fieldnames)
#         self.restval = restval
#
#     @property
#     def fieldnames(self):
#
#         """
#         Return the fieldnames being written
#
#         Returns
#         -------
#         list
#         """
#
#         return self._fieldnames
#
#     def writeheader(self):
#
#         """
#         Write the fieldnames to the output file
#         """
#
#         return self.writer.writerow(self.fieldnames)
#
#     def writerow(self, row):
#
#         """
#         Write a list to the output file.  Only the fields specified by
#         `fieldnames` will be written.
#
#         Parameters
#         ----------
#         row : dict
#
#         """
#
#         return self.writer.writerow([val for val in row if val in self.])
