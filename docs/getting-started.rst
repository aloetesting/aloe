Getting Started
===============

Install Aloe_::

    pip install aloe

Write your first feature ``features/calculator.feature``:

.. code-block:: gherkin

    Feature: Add up numbers

    As a mathematically challenged user
    I want to add numbers
    So that I know the total

    Scenario: Add two numbers
        Given I have entered 50 into the calculator
        And I have entered 30 into the calculator
        When I press add
        Then the result should be 80 on the screen

Features are written using the `Gherkin syntax`_.

Now run ``aloe features/calculator.feature`` and see it fail because there are no
step definitions::

    $ aloe features/calculator.feature
    (...)
    aloe.exceptions.NoDefinitionFound: The step r"Given I have entered 50 into the
    calculator" is not defined

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    FAILED (errors=1)

Now add the definitions in ``features/steps.py``:

.. code-block:: python

    from aloe import before, step, world


    @before.each_example
    def clear(*args):
        """Reset the calculator state before each scenario."""
        world.numbers = []
        world.result = 0


    @step(r'I have entered (\d+) into the calculator')
    def enter_number(self, number):
        world.numbers.append(float(number))


    @step(r'I press add')
    def press_add(self):
        world.result = sum(world.numbers)


    @step(r'The result should be (\d+) on the screen')
    def assert_result(self, result):
        assert world.result == float(result)

Now it works::

    $ aloe features/calculator.feature
    (...)
    Ran 1 test in 0.001s

    OK

.. include:: links.rst
