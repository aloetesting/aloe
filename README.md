Aloe
----

A [Gherkin][gherkin] runner for Python based on [Nose][nose] and
[Lettuce][lettuce].

Quick start
===========

Install: `pip install aloe`

In `features/calculator.feature`:

```gherkin
Feature: Add up numbers

  As a mathematically challenged user
  I want to add numbers
  So that I know the total

  Scenario: Add two numbers
    Given I have entered 50 into the calculator
    And I have entered 30 into the calculator
    When I press add
    Then the result should be 80 on the screen
```

Now run `aloe features/calculator.feature` and see it fail because there are no
step definitions:


In `features/steps.py`:

```python
from aloe import before, step, world


@before.each_example
def clear(*args):
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
```

This works:

```
$ aloe features/calculator.feature
(...)
Ran 1 test in 0.001s

OK
```

Features
========

The standard [Gherkin syntax][gherkin-syntax] is supported, including scenario
outlines, doc strings, data tables and internationalization.

Feature and scenario tags can be used, but aren't currently doing anything.

Steps
=====

Steps are defined in Python using the `step` decorator. The primary method for
defining a step is using the `step` decorator:

```python
from aloe import step

@step(r'The (\w+) is (\w+)')
def has_color(self, object, color):
    # ...
```

### Step loading

Steps can and should be defined in separate modules to the main application
code. Aloe searches for modules upwards from the directory of the feature, for
example, given a feature of `features/calculator/basic/addition.feature`, the
following directories will be searched for modules to import:

* `features/calculator/basic`
* `features/calculator`
* `features`

and so on (the search does not stop at the current directory).

The first directory containing any Python modules stops the search, all the
modules from it are imported and then the feature is run.

If multiple features are given, steps are searched relative to all of them, but
any given module is only imported once.

### Step objects

Each step definition function receives the step object as the first argument.

Callbacks
=========

Invocation
==========

Migrating from Lettuce
======================

TODO
====

* Feature and scenario tags should be converted to Nose tags

[gherkin]: https://cucumber.io/
[nose]: https://nose.readthedocs.org/
[lettuce]: http://lettuce.it/
[gherkin-syntax]: https://cucumber.io/docs/reference
