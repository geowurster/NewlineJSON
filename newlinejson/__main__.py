"""
Enable the CLI interface with `python -m newlinejson`.
"""


import codecs
import csv
import itertools as it
import json
import logging
import os

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


def _cb_quoting(ctx, param, value):
    """Map quoting parameter to CSV library values."""
    try:
        return getattr(csv, 'QUOTE_{}'.format(value.upper()))
    except AttributeError:
        raise click.BadParameter("Invalid quoting: {}".format(value))


def _cb_json_lib(ctx, param, value):
    """Import JSON library."""
    try:
        return nlj.tools.get_json_lib(value)
    except ImportError:
        raise click.BadParameter("Unrecognized JSON library: {}".format(value))


skip_failures_opt = click.option(
    '--skip-failures / --no-skip-failures', default=False, show_default=True,
    help="Skip records that cannot be converted.")
json_lib_opt = click.option(
    '--json-lib', metavar='NAME', default='json', show_default=True,
    callback=_cb_json_lib,
    help="Specify which JSON library should be used for encoding and decoding.")


@click.group()
@click.version_option(nlj.__version__)
@click.option(
    '--verbose', '-v',
    count=True,
    help="Increase verbosity.")
@click.option(
    '--quiet', '-q',
    count=True,
    help="Decrease verbosity.")
@click.pass_context
def main(ctx, verbose, quiet):

    """
    NewlineJSON commandline interface.

    Common simple ETL commands for homogeneous data.
    """

    verbosity = verbose - quiet
    ctx.obj = {'log_level': max(10, 30 - 10 * verbosity)}


@main.command()
@click.argument('infile', type=click.File('r'), default='-')
@click.argument('outfile', type=click.File('w'), default='-')
@skip_failures_opt
@json_lib_opt
@click.pass_context
def csv2nlj(ctx, infile, outfile, skip_failures, json_lib):

    """
    Convert a CSV to newline JSON dictionaries.
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(ctx.obj['log_level'])

    for record in csv.DictReader(infile):
        try:
            record = {
                k: _csv_rec_to_nlj_rec(v) for k, v in six.iteritems(record)}
            outfile.write(json_lib.dumps(record) + os.linesep)
        except Exception:
            if not skip_failures:
                raise
            else:
                logger.exception("Skipped record: %s", record)


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
@click.pass_context
def nlj2csv(ctx, infile, outfile, header, skip_failures, quoting, json_lib):

    """
    Convert newline JSON dictionaries to a CSV.

    Defaults to reading from `stdin` and writing to `stdout`.  CSV fields are
    derived from the first record and `null` values are converted to empty
    CSV fields.
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(ctx.obj['log_level'])

    src = nlj.load(infile, json_lib=json_lib)

    # Get the field names from the first record
    first = next(src)

    writer = csv.DictWriter(outfile, first.keys(), quoting=quoting, escapechar='\\')
    if header:
        writer.writerow(dict((fld, fld) for fld in writer.fieldnames))

    for record in it.chain([first], src):

        try:
            record = {
                k: _nlj_rec_to_csv_rec(v) for k, v in six.iteritems(record)}
            writer.writerow(record)
        except Exception:
            if not skip_failures:
                raise
            else:
                logger.exception("Skipped record: %s", record)


if __name__ == '__main__':  # pragma no cover
    main(prog_name='newlinejson')
