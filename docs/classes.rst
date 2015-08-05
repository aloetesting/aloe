Features, Scenarios and Steps
=============================

.. autoclass:: aloe.parser.Feature()
    :members:
    :inherited-members:
    :exclude-members: add_blocks, add_statements, feature

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

    .. attribute:: scenario

        The :class:`Scenario` this step belongs to
