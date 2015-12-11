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

``newlinejson.open()`` produces a file-like object that behaves like Python's
``io.TextIOWrapper``:

.. code-block:: python

    import newlinejson as nlj

    with nlj.open('sample-data/dictionaries.json') as src:
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

Python's built in JSON library gets the job done, but it is not nearly as fast
as some of the alternatives.  Any JSON decoder supporting ``lib.dumps()`` and
``lib.loads()`` can be used instead of ``json`` via the ``json_lib`` parameter.
To make it easier to support this feature in CLI applications, the name of the
library can also be supplied as a string:

.. code-block:: python

    import newlinejson as nlj
    import ujson

    with nlj.open('sample-data/dictionaries.json', json_lib=ujson) as src:
        with nlj.open('out.json', 'w', json_lib='simplejson') as dst:
            for line in src:
                dst.write(line)


Command Line Interface
======================

This project is primarily intended to be an I/O library, but it does contain a
CLI for performing, simple, common format translations.  The data is expected
to be "square", meaning that newline JSON records must all contain the same
keys, and CSV's must not be jagged.

The CLI requires some additional dependencies, which can be installed with:
``pip install NewlineJSON[cli]``.  The square brackets need to be escaped in
some shells.

Since the CLI is a bonus non-core tool, it is accessed from ``python -m newlinejson``:

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


Installing
==========

Via pip:

.. code-block:: console

    $ pip install NewlineJSON

    # For CLI dependencies:
    $ pip install NewlineJSON[cli]

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
    $ pip install -e .[all]
    $ py.test tests --cov newlinejson --cov-report term-missing
    $ pep8 --max-line-length=95 newlinejson


License
=======

See ``LICENSE.txt``


Changelog
=========

See ``CHANGES.md``
