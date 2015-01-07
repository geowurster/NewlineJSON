"""
NewlineJSON utility: newlinejson
"""


import sys

import click

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

    return dict(pair.split('=') for pair in key_vals)


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
    NewlineJSON commandline interface

    \b
    By default the built in Python JSON library is used but it is not
    necessarily the fastest or best option for every use.  Install your
    preferred library and specify it with something like:

        nlj --json simplejson cat Input-File.json

    NewlineJSON is tested against `ujson`, `simplejson`, and `yajl` because
    they support Python 2 and 3.  Other libraries like `jsonlib2` may work,
    and theoretically any library mimicking the built in library's syntax
    will work without an issue, barring language and compilation issues.
    """

    try:
        newlinejson.JSON = __import__(json)
    except ImportError as e:
        click.echo(e.message, err=True)
        sys.exit(1)


# =========================================================================== #
#   Multi-use options
# =========================================================================== #

reader_options = click.option(
    '-ro', '--reader-option', nargs=-1, metavar='KEY=VAL', default=(),
    help='Keyword arguments to be passed to the reader'
)
writer_options = click.option(
    '-wo', '--writer-option', nargs=-1, metavar='KEY=VAL', default=(),
    help='Keyword arguments to be passed to the writer'
)


# --------------------------------------------------------------------------- #
#   Subcommand: cat
# --------------------------------------------------------------------------- #

@main.command()
@click.argument(
    'input_file', metavar='infile.json', type=click.File(), required=True
)
@reader_options
@writer_options
@click.pass_context
def cat(ctx, input_file, reader_option, writer_option):

    """
    Print the contents of a file
    """

    reader_option = parse_key_vals(reader_option)
    writer_option = parse_key_vals(writer_option)

    try:

        writer = newlinejson.Writer(sys.stdout, **writer_option)
        for line in newlinejson.Reader(input_file, **reader_option):
            writer.writerow(line)
        sys.exit(0)

    except Exception as e:
        click.echo(e.message, err=True)
        sys.exit(1)
