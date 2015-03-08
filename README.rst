===========
NewlineJSON
===========

Streaming newline delimited JSON I/O.

.. image:: https://travis-ci.org/geowurster/NewlineJSON.svg?branch=master
    :target: https://travis-ci.org/geowurster/NewlineJSON

.. image:: https://coveralls.io/repos/geowurster/NewlineJSON/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/NewlineJSON?branch=master


Examples
========

Read and write files with a single JSON object on every line.  See the
``sample-data`` directory for valid input examples.

One dictionary per line:

.. code-block:: python

    from pprint import pprint
    import newlinejson

    with open('sample-data/dictionaries.json') as i_f, open('outfile.json', 'r+') as o_f:
        writer = newlinejson.Writer(o_f)
        for line in newlinejson.Reader(i_f):
            writer.write(line)
        o_f.seek(0)
        pprint(newlinejson.load(o_f))
    [{'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'}
     {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'}
     {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'}
     {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'}
     {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}]

One list per line:

.. code-block:: python

    import newlinejson

    with open('sample-data/lists-no-header.json') as f:
        for line in newlinejson.Reader(f):
            print(line)
    ['l1f2', 'l1f3', 'l1f1']
    ['l2f2', 'l3f3', 'l2f1']
    ['l3f2', 'l3f3', 'l3f1']
    ['l4f2', 'l4f3', 'l4f1']
    ['l5f2', 'l5f3', 'l5f1']

Mixed content:

.. code-block:: python

    import newlinejson

    with open('sample-data/mixed-content.json') as f:
        for line in newlinejson.Reader(f):
            print(line)
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

The standard JSON functions ``load/s()`` and ``dump/s()`` are still available but
should only be used on small files. The ``load/s()`` functions return lists of
JSON objects and ``dump/s()`` take the the same format as input.

Load from a file:

.. code-block:: python

    from pprint import pprint
    import newlinejson

    with open('sample-data/dictionaries.json') as f:
        pprint(newlinejson.load(f))
    [{'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
     {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
     {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
     {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
     {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}]

Load from a string:

.. code-block:: python

    from pprint import pprint
    import newlinejson

    with open('sample-data/dictionaries.json') as f:
        pprint(newlinejson.loads(f.read()))
    [{'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
     {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
     {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
     {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
     {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}]

Dump to a file or a string:

.. code-block:: python

    from pprint import pprint
    import newlinejson

    lines = [
        {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
        {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
        {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
        {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
        {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}
    ]

    with open('output.json', 'r+') as f:
        newlinejson.dump(lines, f)
        f.seek(0)
        pprint(newlinejson.dumps(f.read()))
    [{'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'},
     {'field2': 'l2f2', 'field3': 'l3f3', 'field1': 'l2f1'},
     {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'},
     {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'},
     {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}]


Dependencies
============

NewlineJSON has no dependencies but if Python's built-in JSON library is too slow
it can be used in conjunction with a 3rd party library like ``ujson`` or
``simplejson``.  When available all unittests are run against ``json``, ``ujson``,
``simplejson``, ``yajl``, and ``jsonlib2``.  The internal JSOn library can be
specified like so:

.. code-block:: python

    import newlinejson
    import ujson

    newlinejson.JSON = ujson
    with open('sample-data/dictionaries.json') as f:
        reader = newlinejson.Reader(f)
        print(reader.json_lib.__name__)
    ujson

The library can also be specified for ``load/s()``, ``dump/s()`` ``Reader`` and
``Writer`` via a ``json_lib`` keyword argument:

.. code-block:: python

    from pprint import pprint
    import newlinejson
    import ujson

    with open('sample-data/dictionaries.json') as f:
        reader = newlinejson.Reader(f, json_lib=ujson)
        print(reader.json_lib.__name__)
    ujson

    with open('sample-data/dictionaries.json') as f:
        pprint(newlinejson.load(f, json_lib=ujson))
    [{'field1': 'l1f1', 'field2': 'l1f2', 'field3': 'l1f3'},
     {'field1': 'l2f1', 'field2': 'l2f2', 'field3': 'l2f3'},
     {'field1': 'l3f1', 'field2': 'l3f2', 'field3': 'l3f3'},
     {'field1': 'l4f1', 'field2': 'l4f2', 'field3': 'l4f3'},
     {'field1': 'l5f1', 'field2': 'l5f2', 'field3': 'l5f3'}]


Installing
==========

Via pip:

.. code-block:: console

    $ pip install newlinejson

From master:

.. code-block:: console

    $ git clone https://github.com/geowurster/NewlineJSON.git
    $ cd NewlineJSON
    $ python setup.py install


Developing
==========

Install:

.. code-block:: console

    $ pip install virtualenv
    $ git clone https://github.com/geowurster/NewlineJSON
    $ cd NewlineJSON
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .
    $ nosetests --with-coverage


Profiling
=========

Attempts to profile against: `json`, `jsonlib2`, `simplejson`, `ujson`, and
`yajl`.  A small-ish file is used by default from `sample-data` but the user
can specify any newline delimited JSON file input file as the first argument.

.. code-block:: console

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
