"""
NewlineJSON utility: newlinejson
"""


import sys

import click

import newlinejson
from newlinejson.cli import options


# =========================================================================== #
#   Command group: main
# =========================================================================== #

@click.group()
@click.option(
    '-j', '--json', metavar='LIB', default='json',
    help="Specify which JSON library to use by name"
)
@options.version
@options.license
@click.pass_context
def main(ctx, json):

    """
    NewlineJSON commandline interface
    """

    try:
        newlinejson.JSON = __import__(json)
    except ImportError as e:
        click.echo(e.message, err=True)
        sys.exit(1)
