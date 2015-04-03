"""
Easy access to sample datasets for testing
"""


import os

HUNDRED_K_MIXED_GZ_PATH = os.path.join('sample-data', '100k-mixed.json.gz')
HUNDRED_K_MIXED_BZ2_PATH = os.path.join('sample-data', '100k-mixed.json.bz2')
TEN_K_MIXED_BZ2_PATH = os.path.join('sample-data', '10k-mixed.json.bz2')
TEN_K_MIXED_GZ_PATH = os.path.join('sample-data', '10k-mixed.json.gz')
DICTS_JSON_PATH = os.path.join('sample-data', 'dictionaries.json')
DICTS_BZ2_PATH = os.path.join('sample-data', 'dictionaries.json.bz2')
DICTS_GZ_PATH = os.path.join('sample-data', 'dictionaries.json.gz')
LISTS_JSON_PATH = os.path.join('sample-data', 'lists.json')
LISTS_BZ2_PATH = os.path.join('sample-data', 'lists.json.bz2')
LISTS_GZ_PATH = os.path.join('sample-data', 'lists.json.gz')
MIXED_JSON_PATH = os.path.join('sample-data', 'mixed-content.json')
MIXED_BZ2_PATH = os.path.join('sample-data', 'mixed-content.json.bz2')
MIXED_GZ_PATH = os.path.join('sample-data', 'mixed-content.json.gz')


SMALL_FILES = [
    HUNDRED_K_MIXED_GZ_PATH,
    HUNDRED_K_MIXED_BZ2_PATH,
    TEN_K_MIXED_GZ_PATH,
    TEN_K_MIXED_BZ2_PATH,
    DICTS_JSON_PATH,
    DICTS_BZ2_PATH,
    DICTS_GZ_PATH,
    LISTS_JSON_PATH,
    LISTS_BZ2_PATH,
    LISTS_GZ_PATH,
    MIXED_JSON_PATH,
    MIXED_BZ2_PATH,
    MIXED_GZ_PATH
]


ZIP_GROUPS = {}
for path in SMALL_FILES:
    prefix = path.split('.')[0]
    if prefix not in ZIP_GROUPS:
        ZIP_GROUPS[prefix] = [path]
    else:
        ZIP_GROUPS[prefix].append(path)
