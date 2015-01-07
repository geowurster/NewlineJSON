#!/usr/bin/env python


"""
Unittests for newlinejson.core
"""


from __future__ import unicode_literals

import os
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import sys
import unittest

import json
import simplejson
import ujson
import yajl

import newlinejson


JSON_LIBRARIES = [json, simplejson, ujson, yajl]


SAMPLE_FILE_CONTENTS = {
    'list_with_header': os.linesep.join(
        [json.dumps(i) for i in (["field1", "field2", "field3"],
                                 ["l1f1", "l1f2", "l1f3"],
                                 ["l2f1", "l2f2", "l3f3"],
                                 ["l3f1", "l3f2", "l3f3"])]),
    'list_no_header': os.linesep.join(
        [json.dumps(i) for i in (["l1f1", "l1f2", "l1f3"],
                                 ["l2f1", "l2f2", "l3f3"],
                                 ["l3f1", "l3f2", "l3f3"])]),
    'dict_lines': os.linesep.join(
        [json.dumps(i) for i in ({"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"},
                                 {"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"},
                                 {"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"})])
}


# StringIO in Python 2 requires unicode
if sys.version_info[0] is 2:
    SAMPLE_FILE_CONTENTS = {unicode(k): unicode(v) for k, v in SAMPLE_FILE_CONTENTS.items()}


class TestReader(unittest.TestCase):

    def test_standard(self):

        # Test standard use cases for all file types and JSON libraries
        for json_lib in JSON_LIBRARIES:

            # Test with all JSON libraries
            newlinejson.JSON = json_lib

            # Test with all kinds of content
            for content in SAMPLE_FILE_CONTENTS.values():

                # Prep test file objects and compare every line
                with StringIO(content) as e_f, StringIO(content) as a_f:
                    for expected, actual in zip(e_f, newlinejson.Reader(a_f)):
                        self.assertEqual(json.loads(expected), actual)

    def test_readline(self):

        # The readline method should always return a stripped line

        line = 'words_and_stuff'
        with StringIO(' ' + line + ' ') as f:
            reader = newlinejson.Reader(f)
            self.assertEqual(line, reader._readline())

    def test_skip_lines(self):

        # Skip the first line and only test against the second

        for json_lib in JSON_LIBRARIES:
            for content in SAMPLE_FILE_CONTENTS.values():

                with StringIO(content) as e_f, StringIO(content) as a_f:

                    reader = newlinejson.Reader(a_f, skip_lines=1)

                    # Skip the first line and grab the second line for testing
                    e_f.readline()
                    expected_line = json_lib.loads(e_f.readline().strip())
                    e_f.seek(0)

                    # The reader should skip the first line and return the second
                    actual_line = reader.next()
                    self.assertEqual(expected_line, actual_line)

    def test_bad_line_exception(self):

        # Lines that cannot be decoded by JSON should throw an exception by default

        for json_lib in JSON_LIBRARIES:
            newlinejson.JSON = json_lib

            with StringIO('[') as f:
                reader = newlinejson.Reader(f)
                self.assertRaises(ValueError, reader.next)

    def test_bad_line_no_exception(self):

        # The skip_failures argument should cause a bad line to be skipped and the fail_val to be returned

        for json_lib in JSON_LIBRARIES:

            newlinejson.JSON = json_lib

            for fail_val in [None, 1, 1.23, float, int, object, '', str, {}, []]:
                with StringIO('[') as f:
                    reader = newlinejson.Reader(f, skip_failures=True, fail_val=fail_val)
                    self.assertEqual(reader.next(), fail_val)

    def test_empty_line(self):

        # If skip_empty=False then some user-defined value is returned instead of an empty line
        for json_lib in JSON_LIBRARIES:

            newlinejson.JSON = json_lib

            for empty_val in [None, 1, 1.23, float, int, object, '', str, {}, []]:
                with StringIO(' ') as f:
                    reader = newlinejson.Reader(f, skip_empty=False, empty_val=empty_val)
                    self.assertEqual(reader.next(), empty_val)

    def test_skip_empty(self):

        # Empty lines should be completely skipped

        for json_lib in JSON_LIBRARIES:

            newlinejson.JSON = json_lib

            for content in SAMPLE_FILE_CONTENTS.values():

                # Create some new content that has a bunch of empty lines
                blank = ''
                with StringIO(content) as c1, StringIO(content) as c2:
                    content_lines = c1.readlines() + [blank, blank, blank] + c2.readlines() + [blank]
                content_lines_expected = [line.strip() for line in content_lines if line != blank]

                # At this point content_lines contains some blanks and content_lines_expected contains no blanks
                # and is what the output should look like

                with StringIO(os.linesep.join(content_lines)) as a_f, \
                        StringIO(os.linesep.join(content_lines_expected)) as e_f:
                    reader = newlinejson.Reader(a_f, skip_empty=True)
                    for idx, z in enumerate(zip(reader, e_f)):
                        actual, expected = z
                        expected = json.loads(expected.strip())
                        self.assertEqual(expected, actual)

                    # Make sure no blank lines were read
                    # idx starts at 0 so add 1
                    self.assertEqual(idx + 1, len(content_lines_expected))

    def test_read_mixed_types(self):

        # Read lines of mixed types
        content = os.linesep.join([l.strip() for l in SAMPLE_FILE_CONTENTS.values() if l.strip() != ''])
        for json_lib in JSON_LIBRARIES:
            newlinejson.JSON = json_lib

            with StringIO(content) as a_f, StringIO(content) as e_f:
                reader = newlinejson.Reader(a_f)
                for actual, expected in zip(reader, e_f):
                    expected = json.loads(expected)
                    self.assertEqual(expected, actual)


class TestWriter(unittest.TestCase):

    def test_writerow(self):

        # Try writing every content type
        for json_lib in JSON_LIBRARIES:
            newlinejson.JSON = json_lib

            for content in SAMPLE_FILE_CONTENTS.values():
                with StringIO() as f:
                    writer = newlinejson.Writer(f)

                    # Turn test content into a list of lines
                    content = [json.loads(l) for l in content.split(os.linesep)]

                    # Write each line
                    for line in content:
                        self.assertTrue(writer.writerow(line))

                    # Test each line
                    f.seek(0)
                    for actual, expected in zip(f, content):
                        self.assertEqual(json.loads(actual), expected)

    def test_different_delimiter(self):

        # The user should be able to specify a delimiter of their choice

        new_delim = 'asdfjkl'
        for content in SAMPLE_FILE_CONTENTS.values():
            expected_lines = [json.loads(i) for i in content.split(os.linesep)]
            with StringIO() as f:
                writer = newlinejson.Writer(f, delimiter=new_delim)
                for line in expected_lines:
                    self.assertTrue(writer.writerow(line))

                # Test lines - the writer writes a delimiter to the very end of the file that must be removed in order
                # to compare
                f.seek(0)
                actual = f.read()[:-len(new_delim)]
                expected = new_delim.join([json.dumps(i) for i in expected_lines])
                self.assertEqual(actual, expected)

    def test_bad_lines_throw_exception(self):

        # By default an item `json.dumps()` can't serialize will throw an exception
        with StringIO() as f:
            writer = newlinejson.Writer(f)
            self.assertRaises(TypeError, writer.writerow, newlinejson)

    def test_skip_bad_lines(self):

        # Silently skip items are not JSON serializable
        with StringIO() as f:
            writer = newlinejson.Writer(f, skip_failures=True)
            self.assertTrue(writer.writerow([1, 2, 3]))
            self.assertFalse(writer.writerow(newlinejson))


if __name__ == '__main__':
    sys.exit(unittest.main())
