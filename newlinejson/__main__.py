"""
Enable the CLI interface with `python -m newlinejson`.
"""


import code
import codecs
import csv
from itertools import chain
import json
import os
import sys

import click
import six

import newlinejson as nlj


def _nlj_rec_to_csv_rec(val):

    """
    A more specific `json.dumps()` that only serializes non-string objects to
    prevent double quoting and returns an empty string to prevent `None`'s from
    turning into JSON `null`'s.
    """

    if isinstance(val, six.string_types):
        return val
    elif val is None:
        return ""
    else:
        return json.dumps(val)


def _csv_rec_to_nlj_rec(val):

    """
    Convert a line from `csv.DictReader()` NLJ with `None` instead of empty
    fields.
    """

    val = codecs.decode(val, 'unicode_escape')

    if val == '':
        return None
    elif val.startswith('{'):
        return json.loads(val)
    else:
        return val


skip_failures_opt = click.option(
    '--skip-failures / --no-skip-failures', default=False, show_default=True,
    help="Skip records that cannot be converted.")
json_lib_opt = click.option(
    '--json-lib', metavar='NAME', default='json', show_default=True,
    help="Specify which JSON library should be used for encoding and decoding.")


def _cb_quoting(ctx, param, value):
    """Map quoting parameter to CSV library values."""
    if value == 'all':
        return csv.QUOTE_ALL
    elif value == 'minimal':
        return csv.QUOTE_MINIMAL
    elif value == 'none':
        return csv.QUOTE_NONE
    elif value == 'non-numeric':
        return csv.QUOTE_NONNUMERIC
    else:
        raise click.BadParameter("Bad internal validation")


@click.group()
@click.version_option(nlj.__version__)
def main():

    """
    NewlineJSON commandline interface.

    Common simple ETL commands for homogeneous data.
    """


@main.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.option(
    '--ipython', 'interpreter', flag_value='ipython',
    help="Use IPython as the interpreter.")
def insp(infile, interpreter):  # A good idea borrowed from Rasterio and Fiona

    """
    Open a file and launch a Python interpreter.
    """

    banner = os.linesep.join([
        "NewlineJSON {nljv} Interactive Inspector (Python {pyv}).".format(
            nljv=nlj.__version__, pyv='.'.join(map(str, sys.version_info[:3]))),
        "Type 'help(src)' or 'next(src)' for more information."])

    with nlj.open(infile) as src:  # pragma no cover
        scope = {'src': src}
        if not interpreter:
            code.interact(banner, local=scope)
        elif interpreter == 'ipython':
            import IPython
            IPython.InteractiveShell.banner1 = banner
            IPython.start_ipython(argv=[], user_ns=scope)
        else:
            raise click.ClickException('Interpreter {} is unsupported'.format(interpreter))


@main.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
@skip_failures_opt
@json_lib_opt
def csv2nlj(infile, outfile, skip_failures, json_lib):

    """
    Convert a CSV to newline JSON dictionaries.
    """

    with nlj.open(outfile, 'w', json_lib=json_lib) as dst:
        for record in csv.DictReader(infile):
            try:
                dst.write(
                    dict((k, _csv_rec_to_nlj_rec(v)) for k, v in six.iteritems(record)))
            except Exception:
                if not skip_failures:
                    raise


@main.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
@click.option(
    '--header / --no-header', default=True, show_default=True,
    help="Specify whether the header should be written to the output CSV.")
@skip_failures_opt
@click.option(
    '--quoting', type=click.Choice(['all', 'minimal', 'none', 'non-numeric']),
    default='none', show_default=True, callback=_cb_quoting,
    help="CSV quoting style.  See the Python CSV library documentation for more info.")
@json_lib_opt
def nlj2csv(infile, outfile, header, skip_failures, quoting, json_lib):

    """
    Convert newline JSON dictionaries to a CSV.

    Defaults to reading from `stdin` and writing to `stdout`.  CSV fields are
    derived from the first record and `null` values are converted to empty
    CSV fields.
    """

    with nlj.open(infile, json_lib=json_lib) as src:

        # Get the field names from the first record
        first = next(src)

        writer = csv.DictWriter(outfile, first.keys(), quoting=quoting, escapechar='\\')
        if header:
            writer.writerow(dict((fld, fld) for fld in writer.fieldnames))

        for record in chain([first], src):

            try:
                writer.writerow(
                    dict((k, _nlj_rec_to_csv_rec(v)) for k, v in six.iteritems(record)))
            except Exception:
                if not skip_failures:
                    raise


if __name__ == '__main__':  # pragma no cover
    main(prog_name='newlinejson')
