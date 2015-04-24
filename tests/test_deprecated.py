"""
DEPRECATED - will be removed before v1.0

Unittests for deprecated components of newlinejson
"""


from __future__ import unicode_literals

from imp import reload
import json
import os

import unittest
import warnings

from io import StringIO

import newlinejson
import newlinejson.pycompat


warnings.filterwarnings("ignore")


SAMPLE_FILE_CONTENTS = {
    'list_with_header': os.linesep.join(
        [json.dumps(i) for i in (["field1", "field2", "field3"],
                                 ["l1f1", "l1f2", "l1f3"],
                                 ["l2f1", "l2f2", "l2f3"],
                                 ["l3f1", "l3f2", "l3f3"])]),
    'list_no_header': os.linesep.join(
        [json.dumps(i) for i in (["l1f1", "l1f2", "l1f3"],
                                 ["l2f1", "l2f2", "l2f3"],
                                 ["l3f1", "l3f2", "l3f3"])]),
    'dict_lines': os.linesep.join(
        [json.dumps(i) for i in ({"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"},
                                 {"field2": "l2f2", "field3": "l2f3", "field1": "l2f1"},
                                 {"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"})])
}


# StringIO in Python 2 requires unicode
if newlinejson.pycompat.PY2:  # pragma no cover
    SAMPLE_FILE_CONTENTS = {unicode(k): unicode(v) for k, v in SAMPLE_FILE_CONTENTS.items()}


class TestReader(unittest.TestCase):

    def setUp(self):
        reload(newlinejson)  # Make sure JSON is set back to the default

    def test_attributes(self):
        with StringIO() as f:
            reader = newlinejson.Reader(f)
            self.assertTrue(hasattr(reader, '__next__'))
            self.assertTrue(hasattr(reader, 'next'))
            self.assertTrue(hasattr(reader, '__iter__'))
            self.assertEqual(reader.f, f)

    def test_standard(self):
        for content in SAMPLE_FILE_CONTENTS.values():
            # Prep test file objects and compare every line
            with StringIO(content) as e_f, StringIO(content) as a_f:
                reader = newlinejson.Reader(a_f)
                for expected, actual in zip(e_f, reader):
                    self.assertEqual(json.loads(expected), actual)

    def test_readline(self):
        # Does not handle any decoding - just reading and stripping a line
        line = 'words_and_stuff'
        with StringIO(' ' + line + ' ') as f:
            reader = newlinejson.Reader(f)
            self.assertEqual(line, reader._readline())

    def test_skip_lines(self):

        # Skip the first line and only test against the second
        for content in SAMPLE_FILE_CONTENTS.values():

            with StringIO(content) as e_f, StringIO(content) as a_f:

                reader = newlinejson.Reader(a_f, skip_lines=1)

                # Skip the first line and grab the second line for testing
                e_f.readline()
                expected_line = json.loads(e_f.readline().strip())
                e_f.seek(0)

                # The reader should skip the first line and return the second
                actual_line = reader.next()
                self.assertEqual(expected_line, actual_line)

    def test_bad_line_exception(self):
        # Lines that cannot be decoded by JSON should throw an exception by default
        with StringIO('[') as f:
            reader = newlinejson.Reader(f)
            self.assertRaises(ValueError, reader.next)
            self.assertEqual(1, reader.failures)

    def test_bad_line_no_exception(self):

        # The skip_failures argument should cause a bad line to be skipped and the fail_val to be returned
        for fail_val in [None, 1, 1.23, float, int, object, '', str, {}, []]:
            with StringIO('[') as f:
                reader = newlinejson.Reader(f, skip_failures=True, fail_val=fail_val)
                self.assertEqual(reader.next(), fail_val)

    def test_empty_line(self):
        # If skip_empty=False then some user-defined value is returned instead of an empty line
        for empty_val in [None, 1, 1.23, float, int, object, '', str, {}, []]:
            with StringIO(' ') as f:
                reader = newlinejson.Reader(f, skip_empty=False, empty_val=empty_val)
                self.assertEqual(reader.next(), empty_val)

    def test_skip_empty(self):

        # Empty lines should be completely skipped
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
                idx = None
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
        with StringIO(content) as a_f, StringIO(content) as e_f:
            reader = newlinejson.Reader(a_f)
            for actual, expected in zip(reader, e_f):
                expected = json.loads(expected)
                self.assertEqual(expected, actual)

    def test_default_json_lib(self):
        with StringIO() as f:
            reader = newlinejson.Reader(f)
            self.assertEqual(reader.json_lib, json)

    def test_explicitly_assign_json_lib(self):
        with StringIO() as f:
            reader = newlinejson.Reader(f, json_lib=json)
            self.assertEqual(reader.json_lib, json)


class TestWriter(unittest.TestCase):

    def setUp(self):
        reload(newlinejson)  # Make sure JSON is set back to the default

    def test_attributes(self):
        with StringIO() as f:
            writer = newlinejson.Writer(f)
            self.assertTrue(hasattr(writer, 'writerow'))
            self.assertTrue(hasattr(writer, 'write'))
            self.assertEqual(writer.f, f)

    def test_writerow(self):

        # Try writing every content type
        for content in SAMPLE_FILE_CONTENTS.values():
            with StringIO() as f:
                writer = newlinejson.Writer(f)

                # Turn test content into a list of lines
                content = [json.loads(l) for l in content.split(os.linesep)]

                # Write each line
                for line in content:
                    self.assertTrue(writer.write(line))

                # Test each line
                f.seek(0)
                for actual, expected in zip(f, content):
                    self.assertEqual(json.loads(actual), expected)

    def test_different_delimiter(self):

        # The user should be able to specify a delimiter of their choice

        new_delim = 'a_s_d_f_j_k_l'
        for content in SAMPLE_FILE_CONTENTS.values():
            expected_lines = [json.loads(i) for i in content.split(os.linesep)]
            with StringIO() as f:
                writer = newlinejson.Writer(f, delimiter=new_delim)
                for line in expected_lines:
                    self.assertTrue(writer.write(line))

                # Test lines - the writer writes a delimiter to the very end of the file that must be removed in order
                # to compare
                f.seek(0)
                actual = f.read()
                expected = new_delim.join([json.dumps(i) for i in expected_lines]) + new_delim
                self.assertEqual(actual, expected)

    def test_bad_lines_throw_exception(self):

        # By default an item `json.dumps()` can't serialize will throw an exception
        with StringIO() as f:
            writer = newlinejson.Writer(f)
            self.assertRaises(TypeError, writer.write, newlinejson)
            self.assertEqual(1, writer.failures)

    def test_skip_bad_lines(self):

        # Silently skip items are not JSON serializable
        with StringIO() as f:
            writer = newlinejson.Writer(f, skip_failures=True)
            self.assertTrue(writer.write([1, 2, 3]))
            self.assertFalse(writer.write(newlinejson))

    def test_default_json_lib(self):
        with StringIO() as f:
            writer = newlinejson.Writer(f, json_lib=None)
            self.assertEqual(writer.json_lib, json)

    def test_explicitly_assign_json_lib(self):
        with StringIO() as f:
            writer = newlinejson.Writer(f, json_lib=json)
            self.assertEqual(writer.json_lib, json)
