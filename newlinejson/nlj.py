"""
NewlineJSON utility: newlinejson
"""


import csv
import sys

import click
import str2type

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


# =========================================================================== #
#   Multi-use options
# =========================================================================== #

option_reader_options = click.option(
    '-ro', '--reader-option', metavar='KEY=VAL', multiple=True, callback=str2type.click_callback_key_val_dict,
    help='Keyword arguments to be passed to the reader'
)
option_writer_options = click.option(
    '-wo', '--writer-option', metavar='KEY=VAL', multiple=True, callback=str2type.click_callback_key_val_dict,
    help='Keyword arguments to be passed to the writer'
)
option_infile = click.argument(
    'infile', required=True, type=click.File(mode='r')
)
option_outfile = click.argument(
    'outfile', required=True, type=click.File(mode='w')
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
@option_infile
@option_reader_options
@option_writer_options
@click.pass_context
def cat(ctx, infile, reader_option, writer_option):

    """
    Print the contents of a file.
    """

    try:

        writer = newlinejson.Writer(sys.stdout, **writer_option)
        for line in newlinejson.Reader(infile, **reader_option):
            writer.write(line)
        sys.exit(0)

    except Exception as e:
        click.echo(e.message, err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Subcommand: load
# --------------------------------------------------------------------------- #

@main.command()
@option_outfile
@option_reader_options
@option_writer_options
@click.pass_context
def load(ctx, outfile, reader_option, writer_option):
    
    """
    Dump newline JSON from stdin to a file.
    """
    try:

        writer = newlinejson.Writer(outfile, **writer_option)
        for line in newlinejson.Reader(sys.stdin, **reader_option):
            writer.write(line)
        sys.exit(0)

    except Exception as e:
        click.echo(e.message, err=True)
        sys.exit(1)
