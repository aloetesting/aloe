Writing Features
================

The standard `Gherkin syntax`_ is supported, including scenario
outlines, doc strings, data tables and internationalization.

Feature and scenario tags can be used and are converted to Nose tags, see
docs for the `Attribute selector plugin`_.

Feature Loading
---------------

If features are not specified on the command line, Aloe will look for features
in directories that:

 * Are named ``features``;
 * Are located in a directory containing packages, that is, all their parent
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
