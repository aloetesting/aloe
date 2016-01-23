Features, Scenarios and Steps
=============================

.. toctree::
    :maxdepth: 2

Feature
-------

.. autoclass:: aloe.parser.Feature()
    :members:
    :inherited-members:
    :exclude-members: add_blocks, add_statements, feature, represent_tags,
        background_class, scenario_class, text, max_length

Background
----------

.. autoclass:: aloe.parser.Background()
    :members:
    :inherited-members:
    :exclude-members: add_statements, represented, step_class, text, max_length

    .. attribute:: feature

        The :class:`Feature` this scenario belongs to.

Scenario
--------

.. autoclass:: aloe.parser.Scenario()
    :members:
    :inherited-members:
    :exclude-members: solved_steps, represented, represent_tags,
        represent_outlines, step_class, evaluated, text, max_length

    .. attribute:: name

        The name of this scenario.

    .. attribute:: feature

        The :class:`Feature` this scenario belongs to.

    .. attribute:: outlines

        The examples for this scenario outline as a list of dicts mapping
        column name to value.

Step
----

.. autoclass:: aloe.parser.Step()
    :members:
    :inherited-members:
    :exclude-members: represented, represent_multiline, represent_table,
        resolve_substitutions, step_keyword, text, max_length

    .. attribute:: scenario

        The :class:`Scenario` this step belongs to (if inside a scenario).

    .. attribute:: background

        The :class:`Background` this step belongs to (if inside a background).

    .. attribute:: test

        The instance of :class:`unittest.TestCase` running the current test,
        or None if not currently in a test (e.g. in a
        :func:`~aloe.before.each_feature` callback).

    .. attribute:: testclass

        The :class:`unittest.TestCase` used to run this test. Use
        :attr:`.test` for the *instance* of the test case.

    .. attribute:: passed

        The step passed (used in :class:`after` and :class:`around`).

    .. attribute:: failed

        The step failed (used in :class:`after` and :class:`around`).

    .. method:: behave_as(sentence)

        Execute another step.

        Example:

        .. code-block:: python

            self.behave_as("Given I am at the market")

    .. method:: given(sentence)

        Execute another step.

        Example:

        .. code-block:: python

            self.given("I am at the market")

    .. method:: when(sentence)

        Execute another step.

        Example:

        .. code-block:: python

            self.when("I buy two oranges")

    .. method:: then(sentence)

        Execute another step.

        Example:

        .. code-block:: python

            self.then("I will be charged 60c")

.. include:: links.rst
