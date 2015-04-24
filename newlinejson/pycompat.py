"""
Helpers for supporting multiple versions of Python
"""


import itertools
import sys


if sys.version_info[0] >= 3:  # pragma no cover
    PY2 = False
    string_types = str,
    text_type = str
    zip_longest = itertools.zip_longest
else:  # pragma no cover
    PY2 = True
    string_types = basestring,
    text_type = unicode
    zip_longest = itertools.izip_longest
