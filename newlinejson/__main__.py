"""
Enable the CLI interface with `python -m newlinejson`.
"""


from newlinejson._cli import main

# Import addional commands into the same namespace
from newlinejson.tool import csv2nlj
from newlinejson.tool import nlj2csv


main(prog_name='newlinejson')
