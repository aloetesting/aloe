Hooks
=====

.. toctree::
    :maxdepth: 2

Hooks can be installed to run :attr:`before`, :attr:`around` and :attr:`after`
part of the test.

Hooks can be used to set up and flush test fixtures, apply mocks or capture
failures.

.. class:: aloe.before

    .. decorator:: all

        Run this function before `everything`.

        Example:

        .. code-block:: python

            from aloe import before

            @before.all
            def before_all():
                print("Before all")

    .. decorator:: each_feature

        Run this function before each `feature`.

        :param Feature feature: the feature about to be run

        Example:

        .. code-block:: python

            from aloe import before

            @before.each_feature
            def before_feature(feature):
                print("Before feature")

    .. decorator:: each_example

        Run this function before each `scenario example`.

        :param Scenario scenario: the scenario about to be run
        :param dict outline: the outline of the example about to be run
        :param list steps: the steps about to be run

        Example:

        .. code-block:: python

            from aloe import before

            @before.each_example
            def before_example(scenario, outline, steps):
                print("Before example")

    .. decorator:: each_step

        Run this function before each `step`.

        :param Step step: the step about to be run

        Example:

        .. code-block:: python

            from aloe import before

            @before.each_step
            def before_step(step):
                print("Before step")

.. class:: aloe.after

    Run functions `after` an event. See :class:`aloe.before`.

    Example:

    .. code-block:: python

        from aloe import after

        @after.each_step
        def after_step(step):
            print("After step")

.. class:: aloe.around

    Define context managers that run `around` an event.
    See :class:`aloe.before`.

    Example:

    .. code-block:: python

        from contextlib import contextmanager

        from aloe import around

        @around.each_step
        @contextmanager
        def around_step(step):
            print("Before step")
            yield
            print("After step")

.. include:: world.rst
.. include:: links.rst
