Writing Features
================

.. toctree::
    :maxdepth: 2

The standard `Gherkin syntax`_ is supported, including scenario
outlines, doc strings, data tables and internationalization.

Feature
-------

A feature is a single file that typically defines a single story.
It has a name and an optional description, an optional background_ and many
scenarios.

.. code-block:: gherkin

    Feature: Search

        As a user
        I want to do a search for something not in the default categories
        So that I can provide more detailed search parameters

A feature may also have tags_.

Background
----------

The background_ is an optional section that is run before every scenario and
contains steps. It is used to set up fixtures common to each scenario_ of
the feature_.

A background does not have a name or tags.

If a step fails during the background the scenario will fail.

.. code-block:: gherkin

        Background:
            Given my location is Melbourne, Victoria

Scenario
--------

Scenarios are the individual tests that make up a feature_. Scenarios have
a name and may optionally tags_. The scenario consists of a number of steps.

If a step fails the scenario_ will fail.

.. code-block:: gherkin

        Scenario: Check the results
            When I search for "pet food" and press enter

            # A step with a multiline string.
            Then I should see the text:
            """
            1 result found in 0.15 seconds.
            """

            # A step with a table.
            And I should see the results:
                | Name (primaryText) | Description (secondaryText) |
                | Pets Inc           | Your one stop pet shop      |

Scenario Outline
----------------

A scenario outline is a template for building scenarios from the rows of a
table named ``Examples``. Parameters are written in the form ``<Parameter>``,
where each named parameter must be present in the table.

Scenario outlines have a name and may optionally have tags_.

.. code-block:: gherkin

        Scenario Outline: Search is correctly escaped
            When I search for "<Phrase>" and press enter
            Then I should be at <URL>

            Examples:
                | Phrase   | URL                |
                | pets     | /search/pets       |
                | pet food | /search/pet%20food |

Tags
----

Feature and scenario tags are specified using the form ``@tag_name`` and are
converted to Nose attribute tags, and can be run/excluded using :option:`-a`.

.. code-block:: gherkin

    Feature: Search

        @integration
        Scenario: Live server works as expected
            When I search for "pet food"
            Then I should see >1 result

See docs for the `Attribute selector plugin`_ for more information.

Feature Loading
---------------

If features are not specified on the command line, Aloe will look for features
in directories that are both:

 * Named ``features``;
 * Located in a directory containing packages, that is, all their parent
   directories have an ``__init__.py`` file.

For example, given the following directory structure, only
``one``, ``three`` and ``seven`` features will be run:

::

    one/
        __init__.py
        features/
            one.feature
            two/
                three.feature
       examples/
           four.feature
    five/
        __init__.py
        six/
            features/
                seven.feature
    eight/
        nine/
            features/
                ten.feature

``four`` will not be run because it is not in a directory named ``features``.
``ten`` will not be run because its parent directory, ``nine``, is not a
package. This prevents discovering features of dependent packages if they are
in a virtualenv inside the project directory.

.. include:: links.rst
