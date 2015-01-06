#!/usr/bin/env python


"""
Unittests for newlinejson.core
"""


from __future__ import unicode_literals

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


LIST_WITH_HEADER = """["field1","field2","field3"]
["l1f1","l1f2","l1f3"]
["l2f1","l2f2","l3f3"]
["l3f1","l3f2","l3f3"]"""


LIST_NO_HEADER = """["l1f1","l1f2","l1f3"]
["l2f1","l2f2","l3f3"]
["l3f1","l3f2","l3f3"]"""


DICT_LINES = """{"field2": "l1f2", "field3": "l1f3", "field1": "l1f1"}
{"field2": "l2f2", "field3": "l3f3", "field1": "l2f1"}
{"field2": "l3f2", "field3": "l3f3", "field1": "l3f1"}"""


class TestReader(unittest.TestCase):

    def test_list_with_header(self):

        # Read a file that contains only lists and has a header row
        for json_library in JSON_LIBRARIES:
            newlinejson.JSON = json_library
            for expected, actual in zip(StringIO(LIST_WITH_HEADER), newlinejson.Reader(StringIO(LIST_WITH_HEADER))):
                self.assertEqual(json.loads(expected), actual)

    def test_list_no_header(self):

        # Read a file that contains only lists and does not have a header row
        for json_library in JSON_LIBRARIES:
            newlinejson.JSON = json_library
            for expected, actual in zip(StringIO(LIST_NO_HEADER), newlinejson.Reader(StringIO(LIST_NO_HEADER))):
                self.assertEqual(json.loads(expected), actual)

    def test_dict_lines(self):

        # Read a file that contains only dictionaries on every line
        for json_library in JSON_LIBRARIES:
            newlinejson.JSON = json_library
            for expected, actual in zip(StringIO(DICT_LINES), newlinejson.Reader(StringIO(DICT_LINES))):
                self.assertEqual(json.loads(expected), actual)


if __name__ == '__main__':
    sys.exit(unittest.main())
