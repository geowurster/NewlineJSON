===========
NewlineJSON
===========

Streaming newline delimited JSON I/O.

.. image:: https://travis-ci.org/geowurster/NewlineJSON.svg?branch=master
    :target: https://travis-ci.org/geowurster/NewlineJSON?branch=master

.. image:: https://coveralls.io/repos/geowurster/NewlineJSON/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/NewlineJSON?branch=master


Example
=======

Calling ``newlinejson.open()`` returns a file-like object that behaves like
Python's ``io.TextIOWrapper``:

.. code-block:: python

    import newlinejson as nlj

    with nlj.open('sample-data/dictionaries.json') as src, \
            with nlj.open('out.json', 'w') as dst:
        for line in src:
            dst.write(line)

    with open('out.json') as f:
        print(f.read()))
    {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'}
    {'field2': 'l2f2', 'field3': 'l2f3', 'field1': 'l2f1'}
    {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'}
    {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'}
    {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}


Command Line Interface
======================

Rather than provide another utility, the CLI is accessed from ``python -m newlinejson``:

.. code-block:: console

    $ python -m newlinejson --help
    Usage: newlinejson [OPTIONS] COMMAND [ARGS]...

      NewlineJSON commandline interface.

      Common simple ETL commands for homogeneous data.

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      csv2nlj  Convert a CSV to newline JSON dictionaries.
      insp     Open a file and launch a Python interpreter.
      nlj2csv  Convert newline JSON dictionaries to a CSV.

The included utilities are for working with homogeneous data, meaning that every
line has the same fields.  The goal is to provide simple data translation tools
rather than a more comprehensive suite.


Can't I do everything this module does with one function?
=========================================================

Pretty much - this is the simplest newline delimited JSON API:

.. code-block:: python

    import json

    def reader(stream):
        for line in stream:
            yield json.loads(line)

    with open('sample-data/lists.json') as src, open('outfile.json', 'w') as dst:
        for line in reader(src):
            dst.write(json.dumps(line))

But it doesn't handle failures and every time it needs to be used it has to be
re-written, which means it needs to be packaged, which means it needs unittests,
may as well be a little more Pythonic, and now we're back to this module.  It's
easier and more Pythonic to just ``import newlinejson`` and know that it will
work rather than solve the exact same problem multiple times.


Why is this better than MsgPack, Protobuf, or any other packed-binary format?
=============================================================================

It probably isn't.  If you're looking for a module to incorporate into a high
capacity data pipeline or bandwidth limited environment you definitely want a
packed-binary format.  If you're working with a small amount of local data to
produce a one-off product, proofing a workflow, or want to provide additional
I/O capabilities to a commandline application reading/writing from/to stdin/stdout,
this module is pretty easy to work with.

The goal of this module is to fill a gap in the Python ecosystem in an easy to
use and intuitive manner, not to provide highly optimized I/O.  If Python's
built-in JSON library isn't fast enough but newline delimited JSON is the right
answer to your problem, one of many faster JSON libraries can be used globally with
``newlinejson.core.JSON_LIB = module`` or by setting ``json_lib=module`` as a keyword
argument in ``open()``, ``load()``, etc.


Installing
==========

Via pip:

.. code-block:: console

    $ pip install NewlineJSON

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
    $ pip install -e .[test]
    $ py.test tests --cov newlinejson --cov-report term-missing
    $ pep8 --max-line-length=95 newlinejson


License
=======

See ``LICENSE.txt``


Changelog
=========

See ``CHANGES.md``
