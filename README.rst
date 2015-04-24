===========
NewlineJSON
===========

Streaming newline delimited JSON I/O.

.. image:: https://travis-ci.org/geowurster/NewlineJSON.svg?branch=master
    :target: https://travis-ci.org/geowurster/NewlineJSON

.. image:: https://coveralls.io/repos/geowurster/NewlineJSON/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/NewlineJSON?branch=master


Example
=======

Calling ``newlinejson.open()`` returns a loaded instance of ``newlinejson.Stream()``,
which generally acts like a file-like object.  See ``help(newlinejson.Stream)`` for
more information.

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
may as well be a little more Pythonic, and now we're back to this module.  Add in
transparent compression (in the next version) and its much easier to just
``import newlinejson`` and know that it will work rather than mess with a custom
solution every time.


Why is this better than MsgPack, Protobuf, or any other packed-binary format?
=============================================================================

It probably isn't.  If you're looking for a module to incorporate into a high
capacity data pipeline or bandwidth limited environment you definitely want a
packed-binary format.  If you're working with a small amount of local data to
produce a one-off product, proofing a workflow, or want to provide additional
I/O capabilities to a commandline application reading/writing from/to stdin/
stdout, this module is pretty easy to work with.

The goal of this module is to fill a gap in the Python ecosystem in an easy to
use and intuitive manner, not to provide highly optimized I/O.  If Python's
built-in JSON isn't fast enough but newline delimited JSON is the right answer
to your problem, one of many faster JSON libraries can be used globally with
``newlinejson.core.JSON = module`` or by setting ``json_lib=module`` as a keyword
argument in `open()`, `load()`, etc.


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
    $ pip install -r requirements-dev.txt -e .
    $ nosetests --with-coverage
    $ pep8 --max-line-length=95 newlinejson
