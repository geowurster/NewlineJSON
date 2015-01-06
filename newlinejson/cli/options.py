"""
Options and flags needed by multiple commandline utilities
"""


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


version = click.option('--version', is_flag=True, callback=print_version,
                       expose_value=False, is_eager=True, help="Print version")


license = click.option('--license', is_flag=True, callback=print_license,
                       expose_value=False, is_eager=True, help="Print license")
