"""
Unittests for newlinejson CLI

python -m newlinejson
"""


import csv
import json

from click.testing import CliRunner

import newlinejson as nlj
from newlinejson.__main__ import main, _cb_quoting


def test_csv2nlj(tmpdir, compare_iter, dicts_csv_path, dicts_path):
    outfile = str(tmpdir.mkdir('test').join('out.json'))
    result = CliRunner().invoke(main, [
        'csv2nlj', dicts_csv_path, outfile
    ])
    assert result.exit_code == 0
    with nlj.open(dicts_path) as expected,\
            nlj.open(outfile) as actual:
        compare_iter(expected, actual)


def test_nlj2csv(tmpdir, dicts_path, compare_iter):
    outfile = str(tmpdir.mkdir('test').join('out.csv'))
    result = CliRunner().invoke(main, [
        'nlj2csv', dicts_path, outfile
    ])
    assert result.exit_code == 0
    with nlj.open(dicts_path) as expected, open(outfile) as actual:
        compare_iter(expected, csv.DictReader(actual))


def test_csv2nlj_nulls(tmpdir, compare_iter, dicts_csv_with_null_path, dicts_with_null_path):

    """
    Empty CSV fields should be None when converted to JSON to avoid empty
    strings.
    """

    outfile = str(tmpdir.mkdir('test').join('out.json'))
    result = CliRunner().invoke(main, [
        'csv2nlj', dicts_csv_with_null_path, outfile
    ])
    assert result.exit_code == 0
    with nlj.open(dicts_with_null_path) as expected, nlj.open(outfile) as actual:
        compare_iter(expected, actual)


def test_nlj2csv_nulls(tmpdir, dicts_with_null_path):

    """
    Null JSON fields should become empty CSV fields
    """

    outfile = str(tmpdir.mkdir('test').join('out.csv'))
    result = CliRunner().invoke(main, [
        'nlj2csv', dicts_with_null_path, outfile
    ])
    assert result.exit_code == 0
    with nlj.open(dicts_with_null_path) as expected, open(outfile) as actual:
        for e, a in zip(expected, csv.DictReader(actual)):
            assert a == {k: v if v else "" for k, v in a.items()}

    # Double check that None was not written to a CSV field
    with open(outfile) as f:
        data = f.read()
        assert len(data) > 0
        assert 'None' not in data


def test_encode_json_strings(tmpdir):
    """Ensure that JSON values are preserved beteen NLJ and CSV."""
    infile = str(tmpdir.mkdir('test-in').join('in.json'))
    outfile = str(tmpdir.mkdir('test-out').join('out.json'))
    roundtrip_file = str(tmpdir.mkdir('test-roundtrip').join('roundtrip.json'))

    # Write NLJ where a value is a dictionary to a file and convert to a CSV
    expected = {
        'field1': 'value',
        'field2': {'key': 'val'}
    }
    with nlj.open(infile, 'w') as dst:
        dst.write(expected)
    result = CliRunner().invoke(main, [
        'nlj2csv', infile, outfile
    ])
    assert result.exit_code == 0

    # Convert the CSV from the previous step back to NLJ
    result = CliRunner().invoke(main, [
        'csv2nlj', outfile, roundtrip_file
    ])
    assert result.exit_code == 0
    with nlj.open(roundtrip_file) as src:
        actual = next(src)

    # Compare JSON -> JSON
    assert expected == actual


def test_insp(dicts_path):
    result = CliRunner().invoke(main, [
        'insp', dicts_path
    ])
    assert result.exit_code == 0


def test_insp_error():
    result = CliRunner().invoke(main, [
        'insp', 'bad-path'
    ])
    assert result.exit_code != 0


def test_csv2nlj_failure(tmpdir):
    infile = str(tmpdir.mkdir('test-in').join('in.json'))
    outfile = str(tmpdir.mkdir('test-out').join('out.json'))

    with nlj.open(infile, 'w') as dst:
        dst.write({'field1': 'value'})
        dst.write({'field2': 'uh-oh'})

    result = CliRunner().invoke(main, [
        'nlj2csv', infile, outfile
    ])
    assert result.exit_code != 0


def test_cb_quoting():
    assert _cb_quoting(None, None, 'all') == csv.QUOTE_ALL
    assert _cb_quoting(None, None, 'minimal') == csv.QUOTE_MINIMAL
    assert _cb_quoting(None, None, 'none') == csv.QUOTE_NONE
    assert _cb_quoting(None, None, 'non-numeric') == csv.QUOTE_NONNUMERIC
