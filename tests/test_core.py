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
    'list_with_header': os.linesep.join(['["field1","field2","field3"]',
                                         '["l1f1","l1f2","l1f3"]',
                                         '["l2f1","l2f2","l3f3"]',
                                         '["l3f1","l3f2","l3f3"]']),
    'list_no_header': os.linesep.join(['["l1f1","l1f2","l1f3"]',
                                       '["l2f1","l2f2","l3f3"]',
                                       '["l3f1","l3f2","l3f3"]']),
    'dict_lines': os.linesep.join(['{"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}',
                                   '{"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"}',
                                   '{"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"}'])
}


class TestReader(unittest.TestCase):

    def test_readline(self):

        # The readline method should always return a stripped line

        line = 'words_and_stuff'
        with StringIO(' ' + line + ' ') as f:
            reader = newlinejson.Reader(f)
            self.assertEqual(line, reader._readline())

    def test_standard(self):

        # Test standard use cases for all file types and JSON libraries
        for json_library in JSON_LIBRARIES:

            # Test with all JSON libraries
            newlinejson.JSON = json_library

            # Test with all kinds of content
            for content in SAMPLE_FILE_CONTENTS.values():

                # Prep test file objects and compare every line
                with StringIO(content) as e_f, StringIO(content) as a_f:
                    for expected, actual in zip(e_f, newlinejson.Reader(a_f)):
                        self.assertEqual(json.loads(expected), actual)

    def test_skip_lines(self):

        # Skip the first line and only test against the second

        for json_library in JSON_LIBRARIES:
            for content in SAMPLE_FILE_CONTENTS.values():

                with StringIO(content) as e_f, StringIO(content) as a_f:

                    reader = newlinejson.Reader(a_f, skip_lines=1)

                    # Skip the first line and grab the second line for testing
                    e_f.readline()
                    expected_line = json_library.loads(e_f.readline().strip())
                    e_f.seek(0)

                    # The reader should skip the first line and return the second
                    actual_line = reader.next()
                    self.assertEqual(expected_line, actual_line)

    def test_bad_line_exception(self):

        # Lines that cannot be decoded by JSON should throw an exception by default

        for json_library in JSON_LIBRARIES:
            newlinejson.JSON = json_library

            with StringIO('[') as f:
                reader = newlinejson.Reader(f)
                self.assertRaises(ValueError, reader.next)

    def test_bad_line_no_exception(self):

        # The skip_failures argument should cause a bad line to be skipped and the fail_val to be returned

        for json_library in JSON_LIBRARIES:

            newlinejson.JSON = json_library

            for fail_val in [None, 1, 1.23, float, int, object, '', str, {}, []]:
                with StringIO('[') as f:
                    reader = newlinejson.Reader(f, skip_failures=True, fail_val=fail_val)
                    self.assertEqual(reader.next(), fail_val)

    def test_empty_line(self):

        # If skip_empty=False then some user-defined value is returned instead of an empty line
        for json_library in JSON_LIBRARIES:

            newlinejson.JSON = json_library

            for empty_val in [None, 1, 1.23, float, int, object, '', str, {}, []]:
                with StringIO(' ') as f:
                    reader = newlinejson.Reader(f, skip_empty=False, empty_val=empty_val)
                    self.assertEqual(reader.next(), empty_val)

    def test_skip_empty(self):

        # Empty lines should be completely skipped

        for json_library in JSON_LIBRARIES:

            newlinejson.JSON = json_library

            for content in SAMPLE_FILE_CONTENTS.values():

                # Create some new content that has a bunch of empty lines
                blank = ''
                content_lines = StringIO(content).readlines() + [blank, blank, blank] + \
                                StringIO(content).readlines() + [blank]
                content_lines_expected = [line.strip() for line in content_lines if line != blank]

                with StringIO(os.linesep.join(content_lines)) as f:
                    for idx, z in enumerate(zip(newlinejson.Reader(f, skip_empty=True),
                                                StringIO(os.linesep.join(content_lines_expected)))):
                        actual, expected = z
                        expected = json.loads(expected.strip())
                        self.assertEqual(expected, actual)

                    # Make sure no blank lines were read
                    # idx starts at 0 so add 1
                    self.assertEqual(idx + 1, len(content_lines_expected))


if __name__ == '__main__':
    sys.exit(unittest.main())
