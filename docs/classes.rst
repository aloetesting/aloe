Features, Scenarios and Steps
=============================

.. autoclass:: aloe.parser.Feature()
    :members:
    :inherited-members:
    :exclude-members: add_blocks, add_statements, feature

.. autoclass:: aloe.parser.Background()
    :members:
    :inherited-members:
    :exclude-members: add_statements, represented
    
    .. attribute:: feature

        The :class:`Feature` this scenario belongs to

.. autoclass:: aloe.parser.Scenario()
    :members:
    :inherited-members:
    :exclude-members: solved_steps
    
    .. attribute:: name

        The name of this scenario

    .. attribute:: feature

        The :class:`Feature` this scenario belongs to

.. autoclass:: aloe.parser.Step()
    :members:
    :inherited-members:
    :exclude-members: represented

    .. attribute:: scenario

        The :class:`Scenario` this step belongs to (if inside a scenario)

    .. attribute:: background

        The :class:`Background` this step belongs to (if inside a background)

    .. attribute:: testclass

        The :class:`unittest.TestCase` used to run this test.

    .. attribute:: passed

        The step passed (used in :class:`after` and :class:`around`).

    .. attribute:: failed

        The step failed (used in :class:`after` and :class:`around`).

    .. method:: behave_as(sentence) 

        Execute another step.

        .. code-block:: python

            self.behave_as("Given I am at the market")

    .. method:: given(sentence) 

        Execute another step.

        .. code-block:: python

            self.given("I am at the market")

    .. method:: when(sentence) 

        Execute another step.

        .. code-block:: python

            self.when("I buy two oranges")

    .. method:: then(sentence) 

        Execute another step.

        .. code-block:: python

            self.then("I will be charged 60c")
