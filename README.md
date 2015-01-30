NewlineJSON
===========

Currently under development.

Streaming newline delimited JSON I/O

[![Build Status](https://travis-ci.org/geowurster/NewlineJSON.svg?branch=master)](https://travis-ci.org/geowurster/NewlineJSON) [![Coverage Status](https://coveralls.io/repos/geowurster/NewlineJSON/badge.svg)](https://coveralls.io/r/geowurster/NewlineJSON?branch=master)


Overview
--------

Read and write files with a single JSON object on every line.  See the
`sample-data` directory for valid input examples.

One dictionary per line:
    
    >>> import newlinejson
    >>> with open('sample-data/dictionaries.json') as f:
    >>>     for line in newlinejson.Reader(f):
    >>>         print(line)
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
    >>>     content = f.read()
    >>>     print(newlinejson.loads(content))
    [
        {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
        {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
        {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
        {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
        {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ]

Dump to a file or a string:
    
    >>> import newlinejson
    >>> json_lines = [
        {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
        {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
        {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
        {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
        {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ]
    >>> with open('output.json', 'w') as f:
    >>>     newlinejson.dump(json_lines, f)
    >>> print(newlinejson.dumps(json_lines))
    [
        {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
        {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
        {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
        {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
        {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ]


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


Developing
----------

Install:

    $ pip install virtualenv
    $ git clone https://github.com/geowurster/newlinejson
    $ cd newlinejson
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements-dev.txt
    $ pip install -e .

Test:
    
    $ nosetests


Coverage:

    $ nosetests --with-coverage

Lint:

    $ pep8 --max-line-length=120 newlinejson



Profiling
---------

Attempts to profile against: `json`, `jsonlib2`, `simplejson`, `ujson`, and
`yajl`.  A small-ish file is used by default from `sample-data` but the user
can specify any newline delimited JSON file input file as the first argument.

    $ ./utils/profile.py 

    Profiling json ...
      Start time: 23:25:47
      End time: 23:25:49
      Elapsed secs: 1.654891
      Num rows: 10000
    
    Profiling jsonlib2 ...
      Start time: 23:25:49
      End time: 23:25:52
      Elapsed secs: 2.780862
      Num rows: 10000
    
    Profiling simplejson ...
      Start time: 23:25:52
      End time: 23:25:55
      Elapsed secs: 2.905002
      Num rows: 10000
    
    Profiling ujson ...
      Start time: 23:25:55
      End time: 23:25:56
      Elapsed secs: 0.927346
      Num rows: 10000
    
    Profiling yajl ...
      Start time: 23:25:56
      End time: 23:25:58
      Elapsed secs: 2.620200
      Num rows: 10000
