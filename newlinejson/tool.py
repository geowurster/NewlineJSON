"""
Common conversion utilities and a commandline interface.
"""


import code
import csv
import itertools
from itertools import chain
import json
import os
import sys

import click

import newlinejson as nlj
from .pycompat import PY2
from .pycompat import string_types


if PY2:
    map = itertools.imap


def _dump2csv(val):

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


@click.group()
@click.version_option(nlj.__version__)
def _cli():

    """
    NewlineJSON commandline interface.

    Common simple ETL commands for homogeneous data.
    """


@_cli.command()
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


@_cli.command()
@click.argument(
    'infile', default='-'
)
@click.argument(
    'outfile', type=click.File('w'), default='-',
)
@click.option(
    '--header / --no-header', default=True,
    help="Specify whether the header should be written to the output CSV or not. "
         "(default: True)"
)
@click.option(
    '--skip-failures / --no-skip-failures', default=False,
    help="Skip records that cannot be converted. (default: False)"
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
                record = {fld: _dump2csv(record.get(fld)) for fld in writer.fieldnames}
            else:
                record = {k: _dump2csv(v) for k, v in record.items()}

            writer.writerow(record)


@_cli.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.option(
    '--ipython', 'interpreter', flag_value='ipython',
    help="Use IPython as the interpreter."
)
def insp(infile, interpreter):  # A good idea borrowed from Rasterio and Fiona

    """
    Open a file and launch a Python interpreter.
    """

    banner = os.linesep.join([
        "NewlineJSON {nljv} Interactive Inspector (Python {pyv}).".format(
            nljv=nlj.__version__, pyv='.'.join(map(str, sys.version_info[:3]))),
        "Type 'help(src)' or 'next(src)' for more information."])

    with nlj.open(infile) as src:
        scope = {'src': src}
        if not interpreter:
            code.interact(banner, local=scope)
        elif interpreter == 'ipython':
            import IPython
            IPython.InteractiveShell.banner1 = banner
            IPython.start_ipython(argv=[], user_ns=scope)
        else:
            raise click.ClickException('Interpreter {} is unsupported'.format(interpreter))


if __name__ == '__main__':
    _cli()
