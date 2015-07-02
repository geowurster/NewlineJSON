"""
Enable the CLI interface with `python -m newlinejson`.
"""


from ._cli import cli

# Import addional commands into the same namespace
from .tool import csv2nlj
from .tool import nlj2csv


cli(prog_name='newlinejson')
