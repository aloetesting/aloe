Writing Features
================

.. toctree::
    :maxdepth: 2

The standard `Gherkin syntax`_ is supported, including scenario
outlines, doc strings, data tables and internationalization.

Feature and scenario tags can be used and are converted to Nose tags, see
docs for the `Attribute selector plugin`_.

Feature Loading
---------------

If features are not specified on the command line, Aloe will look for features
in directories that are both:

 * Named ``features``;
 * Located in a directory containing packages, that is, all their parent
   directories have an ``__init__.py`` file.

For example, given the following directory structure, only
``one``, ``three`` and ``four`` features will be run:

::

    one/
       __init__.py
       features/
           one.feature
           two/
              three.feature
              four.feature
       examples/
           five.feature
    two/
       features/
           six.feature

``five`` will not be run because it is not in a directory named ``features``.
``six`` will not be run because its parent directory, ``two``, is not a
package. This prevents discovering features of dependent packages if they are
in a virtualenv inside the project directory.

.. include:: links.rst
