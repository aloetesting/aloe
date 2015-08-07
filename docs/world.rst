World
=====

.. toctree::
    :maxdepth: 2

As a convenience, Aloe provides a :class:`world` object that can be used
to store information related to the test process. Typical usage includes
storing the expected results between steps, or objects or functions that are
useful for every step, such as an instance of a Selenium browser.

Aloe does not explicitly reset :class:`world` between scenarios or
features, so any clean-up must be done by the callbacks.

.. class:: aloe.world

    Store arbitrary data. Shared between hooks and steps.

.. include:: links.rst
