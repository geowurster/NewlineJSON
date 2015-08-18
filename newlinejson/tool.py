"""
Common conversion utilities.
"""


import csv
from itertools import chain
import json

import click

from newlinejson._cli import main
import newlinejson as nlj
from newlinejson.pycompat import string_types


def _nlj_rec_to_csv_rec(val):

    """
    A more specific `json.dumps()` that only serializes non-string objects to
    prevent double quoting and returns an empty string to prevent `None`'s from
    turning into JSON `null`'s.
    """

    if isinstance(val, string_types):
        return val
    elif val is None:
        return ""
    else:
        return json.dumps(val)


@main.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
def csv2nlj(infile, outfile):

    """
    Convert a CSV to newline JSON dictionaries.
    """

    with nlj.open(outfile, 'w') as dst:
        for record in csv.DictReader(infile):

            # Take a row from `csv.DictReader()` and prepare it for
            # writing as newline JSON.  Empty strings are converted
            # to `None` and all other values are passed through
            # `json.loads()`.

            out = {}
            for k, v in record.items():
                if isinstance(v, string_types) and len(v) == 0:
                    out[k] = None
                else:
                    try:
                        out[k] = json.loads(v)
                    except ValueError:
                        out[k] = v

            dst.write(out)


@main.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
@click.option(
    '--header / --no-header', default=True, show_default=True,
    help="Specify whether the header should be written to the output CSV."
)
@click.option(
    '--skip-failures / --no-skip-failures', default=False, show_default=True,
    help="Skip records that cannot be converted."
)
def nlj2csv(infile, outfile, header, skip_failures):

    """
    Convert newline JSON dictionaries to a CSV.

    Defaults to reading from stdin and writing to stdout.  CSV fields are
    derived from the first record and .  The intent is to provide a tool for
    converting homogeneous newline delimited JSON dictionaries to a CSV.
    """

    with nlj.open(infile) as src:

        # Get the field names from the first record
        first = next(src)

        writer = csv.DictWriter(outfile, first.keys(), quoting=csv.QUOTE_ALL)
        if header:
            writer.writeheader()

        for record in chain([first], src):

            if skip_failures:
                record = {
                    fld: _nlj_rec_to_csv_rec(record.get(fld)) for fld in writer.fieldnames}
            else:
                record = {
                    k: _nlj_rec_to_csv_rec(v) for k, v in record.items()}

            writer.writerow(record)
