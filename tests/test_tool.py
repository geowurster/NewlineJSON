"""
Unittests for newlinejson.tool
"""


import csv

from click.testing import CliRunner

import newlinejson as nlj
from newlinejson import tool


def test_csv2nlj(tmpdir):
    outfile = str(tmpdir.mkdir('test').join('out.json'))

    result = CliRunner().invoke(tool.csv2nlj, [
        'sample-data/dictionaries.csv',
        outfile
    ])
    assert result.exit_code == 0
    with nlj.open('sample-data/dictionaries.json') as expected,\
            nlj.open(outfile) as actual:
        for e, a in zip(expected, actual):
            assert e == a


def test_nlj2csv(tmpdir):
    outfile = str(tmpdir.mkdir('test').join('out.json'))

    result = CliRunner().invoke(tool.nlj2csv, [
        'sample-data/dictionaries.json',
        outfile
    ])
    assert result.exit_code == 0
    with nlj.open('sample-data/dictionaries.json') as expected, open(outfile) as actual:
        for e, a in zip(expected, csv.DictReader(actual)):
            assert e == a
