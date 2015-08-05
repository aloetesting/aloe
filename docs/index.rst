Aloe: BDD testing via nose
==========================

.. toctree::
   :maxdepth: 2

Aloe is a Gherkin_-based Behaviour Driven Development tool for Python based
on Nose_.

.. include:: getting-started.rst
.. include:: aloe.rst

Defining Steps
==============

.. autofunction:: aloe.step

Hooks
=====

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

Extensions
==========

* `aloe_django`_ -- Django integration for `Aloe`.

History
=======

`Aloe` originally started life as a branch of the Python BDD tool Lettuce_.
Like so many succulants, it grew into so much more than that.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _aloe: https://github.com/koterpillar/aloe
.. _gherkin: https://cucumber.io/
.. _nose: https://nose.readthedocs.org/
.. _nose-plugin-attrib: https://nose.readthedocs.org/en/latest/plugins/attrib.html
.. _lettuce: http://lettuce.it/
.. _`Gherkin syntax`: https://cucumber.io/docs/reference
.. _`aloe_django`: https://github.com/koterpillar/aloe_django
