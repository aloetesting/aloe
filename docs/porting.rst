Porting from Lettuce
====================

.. toctree::
    :maxdepth: 2

Aloe_, started as a fork of Lettuce_, tries to be compatible where it makes
sense. However, there are following incompatible changes:

 * Aloe aims to use compatible `Gherkin syntax`_, as such the following no
   longer work:

   * Using ``"`` to indicate the indent of a multiline string; and
   * Comments after steps.

 * The :func:`each_scenario`, :func:`each_background` and :func:`outline`
   callbacks are removed. Use :func:`each_example`.
 * The :option:`-s` option for running particular scenarios is renamed to
   :option:`-n`.
 * Django-related functionality, including the ``harvest`` command, is moved to a
   separate project, `aloe_django`_.
 * ``terrain.py`` has no particular significance. It will be imported but only
   if it exists at the same directory with the other step definition files, and
   not above it.
 * Scenario outlines must be declared with "Scenario Outline", and scenarios
   without examples must use "Scenario" - Lettuce allowed using either.

.. include:: links.rst
