"""
Unittests for newlinejson.core
"""


import itertools
import json
from . import sample_data

import newlinejson as nlj


def test_standard():

    with nlj.open(sample_data.DICTS_JSON_PATH) as actual, open(sample_data.DICTS_JSON_PATH) as expected:
        for e_line, a_line in zip(expected, actual):
            print(e_line)
            print(a_line)
            assert json.loads(e_line) == a_line


def test_file_matrix():

    for group in sample_data.ZIP_GROUPS.values():
        readers = [nlj.open(_p) for _p in group]

        for r in readers:
            print(r)
            print(next(r))

    raise ValueError

        # for lines in zip(*readers):
        #     for pair in itertools.combinations(lines, 2):
        #         assert pair[0] == pair[1]
        #
        # for r in readers:
        #     r.close()
        #     assert r.closed
        #     assert r._stream.closed
