NewlineJSON
===========

Currently under development.

Streaming newline delimited JSON I/O

[![Build Status](https://travis-ci.org/geowurster/NewlineJSON.svg)](https://travis-ci.org/geowurster/NewlineJSON)


Overview
--------

Read and write files with a single JSON object on every line.  See the
`sample-data` directory for valid input examples.

One dictionary per line:
    
    >>> import newlinejson
    >>> with open('sample-data/dictionaries.json') as f:
    >>>     for line in newlinejson.Reader(f):
    >>>         print(line)
    >>>
    {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'}
    {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'}
    {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'}
    {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'}
    {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}

One list per line:

    >>> import newlinejson
    >>> with open('sample-data/lists-no-header.json') as f:
    >>>     for line in newlinejson.Reader(f):
    >>>         print(line)
    >>>
    ['l1f2', 'l1f3', 'l1f1']
    ['l2f2', 'l3f3', 'l2f1']
    ['l3f2', 'l3f3', 'l3f1']
    ['l4f2', 'l4f3', 'l4f1']
    ['l5f2', 'l5f3', 'l5f1']

Mixed content:

    >>> import newlinejson
    >>> with open('sample-data/mixed-content.json') as f:
    >>>     for line in newlinejson.Reader(f):
    >>>         print(line)
    >>> 
    {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'}
    ['l1f2', 'l1f3', 'l1f1']
    {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'}
    ['l2f2', 'l3f3', 'l2f1']
    {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'}
    ['l3f2', 'l3f3', 'l3f1']
    {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'}
    ['l4f2', 'l4f3', 'l4f1']
    {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ['l5f2', 'l5f3', 'l5f1']

The standard JSON functions `load/s()` and `dump/s()` are still available but
should ONLY be used on small files and are really only included as a convenience.
The `load/s()` functions return lists of JSON objects and `dump/s()`take the
same format.

Load from a file:

    >>> import newlinejson
    >>> with open('sample-data/dictionaries.json') as f:
    >>>     print(newlinejson.load(f))
    >>> 
    [
        {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
        {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
        {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
        {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
        {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ]

Load from a string:

    >>> import newlinejson
    >>> with open('sample-data/dictionaries.json') as f:
    >>>     print(newlinejson.loads(f.read()))
    >>> 
    [
        {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
        {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
        {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
        {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
        {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ]

Dump to a file:
    
    >>> with open('output.json', 'w') as f:
    >>>     newlinejson.dump(json_lines, f)

Dump to a string:
    
    >>> string = newlinejson.dumps(json_lines)


Installing
----------

    $ pip install newlinejson


Developing
----------
    
    $ pip install virtualenv
    $ git clone https://github.com/geowurster/NewlineJSON
    $ cd NewlineJSON
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt -r requirements-dev.txt
    $ nosetests


Testing
-------

Code coverage report

    $ nosetests \
    $     --with-coverage \
    $     --cover-package=newlinejson \
    $     --cover-erase --cover-inclusive

PEP8 report - the default style guide is used except a max line length of 120
is preferred.

    $ pep8 --max-line-length=120 newlinejson
