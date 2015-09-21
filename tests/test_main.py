"""
Unittests for newlinejson.tool
"""


import csv

from click.testing import CliRunner

import newlinejson as nlj
from newlinejson.__main__ import main


def test_csv2nlj(tmpdir, dicts_csv_path, dicts_path):
    outfile = str(tmpdir.mkdir('test').join('out.json'))

    result = CliRunner().invoke(main, [
        'csv2nlj', dicts_csv_path, outfile
    ])
    assert result.exit_code == 0
    with nlj.open(dicts_path) as expected,\
            nlj.open(outfile) as actual:
        for e, a in zip(expected, actual):
            assert e == a


def test_nlj2csv(tmpdir, dicts_path):
    outfile = str(tmpdir.mkdir('test').join('out.json'))

    result = CliRunner().invoke(main, [
        'nlj2csv', dicts_path, outfile
    ])
    assert result.exit_code == 0
    with nlj.open(dicts_path) as expected, open(outfile) as actual:
        for e, a in zip(expected, csv.DictReader(actual)):
            assert e == a
