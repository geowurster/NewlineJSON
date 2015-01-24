"""
NewlineJSON utility: newlinejson
"""


import csv
import sys

import click
from str2type import str2type

import newlinejson


def print_version(ctx, param, value):

    """
    Print version and exit

    Parameters
    ----------
    ctx : click.Context or None
        Parent context
    param : str or None
        Parameter for option
    value : str
        Flag, option, or argument (in this case `--version`)
    """

    if not value or ctx.resilient_parsing:
        return None

    click.echo(newlinejson.__version__)
    ctx.exit()


def print_license(ctx, param, value):

    """
    Print license and exit

    Parameters
    ----------
    ctx : click.Context or None
        Parent context
    param : str or None
        Parameter for option
    value : str
        Flag, option, or argument (in this case `--license`)
    """

    if not value or ctx.resilient_parsing:
        return None

    click.echo(newlinejson.__license__)
    ctx.exit()


def parse_key_vals(key_vals):

    """
    Parse `KEY=VAL` pairs collected from the commandline
    Turns: ``['k1=v1', 'k2=v2']``
    Into: ``{'k1': 'v1', 'k2': 'v2'}``
    Parameters
    ----------
    key_vals : tuple or list
    Raises
    ------
    ValueError
        Key=val pair does not contain an '='
    Returns
    -------
    dict
        Parsed {'key': 'val'} pairs
    """

    for pair in key_vals:
        if '=' not in pair:
            raise ValueError("Key=val pair does not contain an '=': {}".format(pair))

    output = {}
    for k, v in [pair.split('=') for pair in key_vals]:
        output[k] = str2type(v)
    return output


def parse_list(ctx, param, value):

    """
    Parse `field1,field2,...` pairs collected from the commandline
    Turns: `field1,field2,...`
    Into: ``['field1', 'field2']``
    Parameters
    ----------
    ctx : click.Context or None
        Click context
    param : str or None
        Argument/flag/option
    value : str
        Value if `param` is an option
   
    Returns
    -------
    list
    """

    return value.split(',')


def cast(ctx, param, value):
    
    """
    Callback function to cast arguments to their Python type.  The user specifies
    something like `--fields='["f1","f2"]'` and the subcommand function receives
    `['f1', 'f2']`.
    
    Parameters
    -----------
    ctx : click.Context or None
        Click context
    param : str or None
        Argument/flag/option
    value : str
        Value if `param` is an option
    """
    
    return str2type(value)


# =========================================================================== #
#   Multi-use options
# =========================================================================== #

option_reader_options = click.option(
    '-ro', '--reader-option', nargs=-1, metavar='KEY=VAL', default=(),
    help='Keyword arguments to be passed to the reader'
)
option_writer_options = click.option(
    '-wo', '--writer-option', nargs=-1, metavar='KEY=VAL', default=(),
    help='Keyword arguments to be passed to the writer'
)
option_reader = click.option(
    '-r', '--reader', 'reader_name', metavar='NAME', default='newlinejson',
    help='Specify which reader to use'
)
option_writer = click.option(
    '-w', '--writer', 'writer_name', metavar='NAME', default='newlinejson',
    help='Specify which writer to use'
)
option_infile = click.argument(
    'infile', required=True, type=click.File(mode='r')
)
option_outfile = click.argument(
    'outfile', required=True, type=click.File(mode='w')
)
option_input_json_file = click.argument(
    'input_json_file', required=True, type=click.File(mode='r')
)
option_output_json_file = click.argument(
    'output_json_file', required=True, type=click.File(mode='w')
)
option_input_csv_file = click.argument(
    'input_csv_file', required=True, type=click.File(mode='r')
)
option_output_csv_file = click.argument(
    'output_csv_file', required=True, type=click.File(mode='w')
)


# =========================================================================== #
#   Main CLI Group
# =========================================================================== #

@click.group()
@click.option(
    '-j', '--json', metavar='LIB', default='json',
    help="Specify which JSON library to use by name"
)
@click.option(
    '--version', is_flag=True, callback=print_version,
    expose_value=False, is_eager=True, help="Print version"
)
@click.option(
    '--license', is_flag=True, callback=print_license,
    expose_value=False, is_eager=True, help="Print license"
)
@click.pass_context
def main(ctx, json):

    """
    NewlineJSON commandline interface offering limited transformation and
    filtering operations.

    \b
    By default the built in Python JSON library is used but it is not
    necessarily the fastest or best option for every use.  Install your
    preferred library and specify it with something like:

        nlj --json simplejson cat Input-File.json

    NewlineJSON is tested against `ujson`, `simplejson`, and `yajl` because
    they support Python 2 and 3.  Other libraries like `jsonlib2` may work,
    but are untested.  Theoretically any library supporting the JSON standard
    that matches the built-in JSON library's syntax should work without issue.
    """

    try:
        newlinejson.core.JSON = __import__(json)
    except ImportError as e:
        click.echo(e.message, err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Subcommand: cat
# --------------------------------------------------------------------------- #

@main.command()
@option_input_json_file
@option_reader_options
@option_writer_options
@click.pass_context
def cat(ctx, input_json_file, reader_option, writer_option):

    """
    Print the contents of a file.
    """

    try:

        reader_option = parse_key_vals(reader_option)
        writer_option = parse_key_vals(writer_option)

        writer = newlinejson.Writer(sys.stdout, **writer_option)
        for line in newlinejson.Reader(input_json_file, **reader_option):
            writer.write(line)
        sys.exit(0)

    except Exception as e:
        click.echo(e.message, err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Subcommand: load
# --------------------------------------------------------------------------- #

@main.command()
@option_output_json_file
@option_reader_options
@option_writer_options
@click.pass_context
def load(ctx, output_json_file, reader_option, writer_option):
    
    """
    Dump newline JSON from stdin to a file.
    """
    try:

        reader_option = parse_key_vals(reader_option)
        writer_option = parse_key_vals(writer_option)

        writer = newlinejson.Writer(output_json_file, **writer_option)
        for line in newlinejson.Reader(sys.stdin, **reader_option):
            writer.write(line)
        sys.exit(0)

    except Exception as e:
        click.echo(e.message, err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Subcommand: csv2newline
# --------------------------------------------------------------------------- #

@main.command()
@option_input_csv_file
@option_output_json_file
@option_reader_options
@option_writer_options
@click.pass_context
def csv2newline(ctx, input_csv_file, output_json_file, reader_option, writer_option):

    """
    Convert a CSV to newline JSON dictionaries.
    """

    try:

        reader_option = parse_key_vals(reader_option)
        writer_option = parse_key_vals(writer_option)

        writer = newlinejson.Writer(output_json_file, **writer_option)
        for line in csv.DictReader(input_csv_file, **reader_option):
            writer.write(line)

    except Exception as e:

        click.echo(e.message, err=True)
        sys.exit(1)
