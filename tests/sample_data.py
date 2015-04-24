"""
Easy access to sample datasets for testing
"""


import os


HUNDRED_K_MIXED_GZ_PATH = os.path.join('sample-data', '100k-mixed.json.gz')
TEN_K_MIXED_GZ_PATH = os.path.join('sample-data', '10k-mixed.json.gz')
DICTS_JSON_PATH = os.path.join('sample-data', 'dictionaries.json')
DICTS_GZ_PATH = os.path.join('sample-data', 'dictionaries.json.gz')
LISTS_JSON_PATH = os.path.join('sample-data', 'lists.json')
LISTS_GZ_PATH = os.path.join('sample-data', 'lists.json.gz')
MIXED_JSON_PATH = os.path.join('sample-data', 'mixed-content.json')
MIXED_GZ_PATH = os.path.join('sample-data', 'mixed-content.json.gz')


SMALL_FILES = [
    HUNDRED_K_MIXED_GZ_PATH,
    TEN_K_MIXED_GZ_PATH,
    DICTS_JSON_PATH,
    DICTS_GZ_PATH,
    LISTS_JSON_PATH,
    LISTS_GZ_PATH,
    MIXED_JSON_PATH,
    MIXED_GZ_PATH
]


ZIP_GROUPS = {}
for path in SMALL_FILES:
    prefix = path.split('.')[0]
    if prefix not in ZIP_GROUPS:
        ZIP_GROUPS[prefix] = [path]
    else:
        ZIP_GROUPS[prefix].append(path)
