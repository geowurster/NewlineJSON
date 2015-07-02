"""
Unittests for newlinejson.tool
"""


import csv

from click.testing import CliRunner


def test_csv2nlj():

    with open('sample-data/with-null.csv') as f:
        for