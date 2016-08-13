Running Aloe
============

.. toctree::
    :maxdepth: 2

The ``aloe`` helper runs Nose_ with the Aloe_ plugin enabled.

``aloe`` accepts the same flags as ``nosetests`` and so these are not
extensively documented here.

.. program:: aloe

.. option:: <feature>

    Run only the specified feature files.

.. option:: -n N[,N...]

    Only run the specified scenarios (by number, 1-based) in each
    feature. Makes sense when only specifying one feature to run, for example::

        aloe features/calculator.feature -n 1

.. option:: --test-class

    Override the class used as a base for each feature.

.. option:: --no-ignore-python

    Run Python tests as well as Gherkin.

.. option:: --tag attr

    Run features and scenarios with the given tag. Can be used multiple times.

.. option:: --exclude-tag attr

    Run features and scenarios that do not have the given tag. Can be used
    multiple times.

.. include:: links.rst
