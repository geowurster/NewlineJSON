"""
Unittests for newlinejson.nlj
"""


import json
import os
import sys
import tempfile
import unittest

from . import JSON_LIBRARIES
from . import StringIO

import click.testing

import newlinejson
from newlinejson import nlj


class TestParseKeyVals(unittest.TestCase):

    """
    newlinejson.nlj.parse_key_vals()
    """

    def test_parse(self):

        # Turn ['k1=v1', 'k2=v2'] into {'k1': 'v1', 'k2': 'v2'}
        pairs = ['k1=v1', 'k2=v2']
        expected = {'k1': 'v1', 'k2': 'v2'}
        self.assertDictEqual(expected, nlj.parse_key_vals(pairs))

    def test_exception(self):

        # Make sure appropriate exceptions are raised
        self.assertRaises(ValueError, nlj.parse_key_vals, ['no_equals'])


def test_parse_list():

    # A string containing commas should be split into a list of elements
    val = "field1,field2,field3,field4,field5"
    assert nlj.parse_list(None, None, val) == val.split(',')


def test_cast():

    def none(arg):
        if arg.strip().lower() == 'none':
            return None
        else:
            raise ValueError("Not 'none': %s" % arg)

    def true(arg):
        if arg.strip().lower() == 'true':
            return True
        else:
            raise ValueError("Not 'true': %s" % arg)

    def false(arg):
        if arg.strip().lower() == 'false':
            return False
        else:
            raise ValueError("Not 'false': %s" % arg)

    for string, caster in (('1', int), ('1.', float), ('.1', float), ('0.1', float),
                           ('1.0', float), ('StRiNg', str), ('tRuE', true), ('fAlSe', false),
                           ('nOnE', none), ('[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]', json.loads)):
        assert caster(string) == nlj.cast(None, None, string)


class TestGeneralOptions(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile()
        self.runner = click.testing.CliRunner()

    def tearDown(self):
        self.tempfile.close()

    def test_version(self):

        # Check output from the --version flag

        result = self.runner.invoke(nlj.main, ['--version'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(result.output.strip(), newlinejson.__version__.strip())

    def test_license(self):

        # Check output from the --license flag

        result = self.runner.invoke(nlj.main, ['--license'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(result.output.strip(), newlinejson.__license__.strip())

    def test_assign_json_library(self):

        # Declare which JSON library to use
        for json_lib in JSON_LIBRARIES:
            result = self.runner.invoke(nlj.main, ['--json', json_lib.__name__, 'cat', self.tempfile.name])
            self.assertEqual(0, result.exit_code)
            self.assertEqual(json_lib, nlj.newlinejson.core.JSON)

    def test_assign_bad_json_library(self):

        result = self.runner.invoke(nlj.main, ['--json', 'NON EXISTENT LIB', 'cat'])
        self.assertNotEqual(0, result.exit_code)


class TestCat(unittest.TestCase):

    def setUp(self):
        self.runner = click.testing.CliRunner()
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')
        self.lines = [
            {'field1': 'f1l1', 'field2': 'f2l1', 'field3': 'f3l1'},
            {'field1': 'f1l2', 'field2': 'f2l2', 'field3': 'f3l2'},
            {'field1': 'f1l3', 'field2': 'f2l3', 'field3': 'f3l3'}
        ]

    def tearDown(self):
        self.tempfile.close()

    def test_standard(self):

        # Test standard execution
        for line in self.lines:
            self.tempfile.write(json.dumps(line) + os.linesep)
        self.tempfile.seek(0)

        result = self.runner.invoke(nlj.main, ['cat', self.tempfile.name])
        self.assertEqual(0, result.exit_code)

        # The logical test would be to do a string comparison between the output and the original input lines
        # processed into a string but that test fails every so often so instead string is parsed with the reader
        # and each line is compared individually
        with StringIO(result.output.strip()) as decode_f:
            for expected, actual in zip(newlinejson.Reader(decode_f), self.lines):
                self.assertDictEqual(expected, actual)

    def test_exception(self):
        # Encode a JSON object to a string and then force it to be invalid by removing the first character then
        # write it to a file
        self.tempfile.write(json.dumps(self.lines[0])[1:])
        self.tempfile.seek(0)
        result = self.runner.invoke(nlj.main, ['cat', self.tempfile.name])
        self.assertNotEqual(0, result.exit_code)


class TestLoad(unittest.TestCase):

    def setUp(self):
        self.runner = click.testing.CliRunner()
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')
        self.lines = [
            {'field1': 'f1l1', 'field2': 'f2l1', 'field3': 'f3l1'},
            {'field1': 'f1l2', 'field2': 'f2l2', 'field3': 'f3l2'},
            {'field1': 'f1l3', 'field2': 'f2l3', 'field3': 'f3l3'}
        ]

    def tearDown(self):
        self.tempfile.close()

    def test_standard(self):
        input_lines = newlinejson.dumps(self.lines)
        result = self.runner.invoke(nlj.main, ['load', self.tempfile.name], input=input_lines)
        self.assertEqual(0, result.exit_code)
        for actual, expected in zip(newlinejson.Reader.from_string(input_lines), self.lines):
            self.assertDictEqual(expected, actual)

    def test_exception(self):
        # Create bad JSON by chopping off the first character
        input_lines = newlinejson.dumps(self.lines)[1:]
        result = self.runner.invoke(nlj.main, ['load', self.tempfile.name], input=input_lines)
        self.assertNotEqual(0, result.exit_code)
