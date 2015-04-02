===========
NewlineJSON
===========

Streaming newline delimited JSON I/O with transparent compression.

.. image:: https://travis-ci.org/geowurster/NewlineJSON.svg?branch=master
    :target: https://travis-ci.org/geowurster/NewlineJSON

.. image:: https://coveralls.io/repos/geowurster/NewlineJSON/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/NewlineJSON?branch=master


Examples
========

Read and write files with a single JSON object on every line.  See the
``sample-data`` directory for valid input examples.

.. code-block:: python

    import newlinejson as nlj

    with nlj.open('sample-data/dictionaries.json') as src:
        for line in src:
            print(line)
    {'field2': 'l1f2', 'field3': 'l1f3', 'field1': 'l1f1'}
    {'field2': 'l2f2', 'field3': 'l2f3', 'field1': 'l2f1'}
    {'field2': 'l3f2', 'field3': 'l3f3', 'field1': 'l3f1'}
    {'field2': 'l4f2', 'field3': 'l4f3', 'field1': 'l4f1'}
    {'field2': 'l5f2', 'field3': 'l5f3', 'field1': 'l5f1'}


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
