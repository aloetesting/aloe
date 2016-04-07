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

Now run ``aloe features/calculator.feature`` and see it fail because there are
no step definitions:

.. code-block:: console

    $ aloe features/calculator.feature
    (...)
    aloe.exceptions.NoDefinitionFound: The step r"Given I have entered 50 into the
    calculator" is not defined

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    FAILED (errors=1)

Now add the definitions in ``features/__init__.py``:

.. code-block:: python

    from calculator import add

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
        world.result = add(*world.numbers)


    @step(r'The result should be (\d+) on the screen')
    def assert_result(self, result):
        assert world.result == float(result)

And the implementation stub in ``calculator.py``:

.. code-block:: python

    def add(*numbers):
        return 0

Aloe will tell you that there is an error, including the location of the
failing step, as if it was a normal Python test:

.. code-block:: console
    :emphasize-lines: 9,10

    $ aloe features/calculator.feature

    F
    ======================================================================
    FAIL: Add two numbers (features.calculator: Add up numbers)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      (...)
      File ".../features/calculator.feature", line 11, in Add two numbers
        Then the result should be 80 on the screen
      File ".../aloe/registry.py", line 161, in wrapped
        return function(*args, **kwargs)
      File ".../features/__init__.py", line 25, in assert_result
        assert world.result == float(result)
    AssertionError

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    FAILED (failures=1)

Let's implement the function properly:

.. code-block:: python

    def add(*numbers):
        return sum(numbers)

Now it works:

.. code-block:: console

    $ aloe features/calculator.feature
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    OK

.. include:: links.rst
