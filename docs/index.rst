============================
 Aloe: BDD testing via nose
============================

Aloe is a Gherkin_-based Behavior Driven Development tool for Python based
on Nose_.

**Note**: Currently the Windows support for `Aloe` is very provisional.
Since `Aloe` depends on `blessings`_ for its colored terminal output.
Blessings on the other hand depends on the curses library, which does not
have native Windows support. In order to make `Aloe` at least usable under
Windows, colored output is deactivated when the operating system is detected
to be Windows.

.. _blessings: https://github.com/erikrose/blessings

.. toctree::
    :maxdepth: 2

    aloe
    features
    steps
    hooks
    classes
    extras
    extending
    porting

.. include:: getting-started.rst


History
=======

`Aloe` originally started life as a branch of the Python BDD tool Lettuce_.
Like so many succulents, it grew into so much more than that.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
