"""
Main CLI click group.

Must be placed here to avoid import conflicts.
"""


import code
import os
import sys

import click

import newlinejson as nlj


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
