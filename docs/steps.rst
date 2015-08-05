Defining Steps
==============

.. autofunction:: aloe.step(sentence=None)

Step Loading
------------

Steps can and should be defined in separate modules to the main application
code. Aloe searches for modules to load steps from inside the `features`
directories.

Additional 3rd-party steps (such as `aloe_django`_) can be imported in from
your ``__init__.py``.
