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

```
$ aloe features/calculator.feature
(...)
aloe.exceptions.NoDefinitionFound: The step r"Given I have entered 50 into the
calculator" is not defined

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```

Now add the definitions in `features/steps.py`:

```python
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

If `aloe` is run without specifying the features, every file with the extension
of `.feature` in a directory called `features` (and its subdirectories) will be
run.

Steps
=====

Steps are defined in Python using the `step` decorator. The primary method for
defining a step is using the `step` decorator:

```python
from aloe import step

@step(r'The (\w+) is (\w+)')
def has_color(self, thing, color):
    # ...
```

### World

As a convenience, Aloe provides a `world` object that can be used to store
information related to the test process. Typical usage includes storing the
expected results between steps, or objects or functions that are useful for
every step, such as an instance of a Selenium browser.

Aloe does not explicitly reset `world` between scenarios or features, so any
clean-up must be done by the callbacks.

### Step loading

Steps can and should be defined in separate modules to the main application
code. Aloe searches for modules to load steps from inside the `features`
directories found.

### Step objects

Each step definition function receives the step object as the first argument.
Step objects have the following properties:

* `sentence` - the sentence that invoked the step.
* `hashes` - a list of hashes corresponding to the data table, where the first
  table row is assumed to be the keys.
* `table` - the data table as a list of (ordered) lists.
* `scenario` - the scenario containing this step. Not defined for steps that
  are part of a background.
* `background` - the background containing this step. Not defined for steps
  that are part of a scenario.

Callbacks
=========

Aloe provides a way to execute Python code on certain events when running
Gherkin code. A callback can run before, after or wrap the particular event (as
a context decorator).

### Callback events

* `each_step` - running a single step. The callback receives the step object as
  a sole argument.
* `each_example` - running an example, that is, either a standalone scenario,
  or an example in a  scenario outline.Note that this includes running the
  corresponding background. The callback receives the following arguments:
  - `scenario` - the scenario being run. In case of an example in a scenario
    outline, this is the scenario outline with all the example definitions
    filled in.
  - `outline` - a hash of parameters substituted in the scenario outline, or
    `None` if the scenario does not have examples.
  - `steps` - a list of steps in the scenario.
* `each_feature` - running a single feature. Receives the feature object as a
  sole argument.
* `all` - running the whole test suite (or only the features/scenarios
   specified for running). The callback receives no arguments.

Each callback can be executed before, after or around the event. The decorators
above are available on `before`, `after` and `around` objects:

```python
@before.all
def before_all_callback():
    print("This will be executed once before running any features.")


from contextlib import contextmanager
@around.each_feature
@contextmanager
def around_feature_callback(feature):
    print("This will execute once before every feature.")
    yield
    print("This will execute once after every feature.")


@after.each_step
def after_step_callback(step):
    print("This will be executed once after each step runs.")
```

The most specific callbacks run closer to the event than the least specific.
That is, a "before feature" callback will run before a "before example"
callback, but an "after example" callback will run after an "after step"
callback. "Around" callbacks are wrapped similarly - the least specific ones
will be entered into first and exited from last.

Between the same level of callbacks (e.g. feature callbacks), the order is as
follows:

* Before
* Around (entering part)
* The actual event
* Around (exit part)
* After

An optional `priority` argument can be given to the decorators to establish
priority between the same type and level of callbacks. Default priority is 0.
Lower priority means farther from the event - a "before" callback with a
priority of 1 will run later than a "before" callback with a zero priority,
but an "after" callback with run earlier.

Order of running callbacks of the same type, level and priority is unspecified.

Invocation
==========

`aloe` command line tool is a wrapper for the `nose` runner, configured to only
run Gherkin tests. As such, the invocation is the same as `nose`, but the
following parameters are added:

* `-n N[,N...]` - only run the specified scenarios (by number, 1-based) in each
  feature. Makes sense when only specifying one feature to run, for example

  `aloe features/calculator.feature -n 1`

* `--test-class` - override the class used as a base for each feature.

* `--no-ignore-python` - run Python tests as well as Gherkin.

Migrating from Lettuce
======================

Aloe, started as a fork of Lettuce, tries to be compatible where it makes
sense. However, there are following incompatible changes:

* `each_scenario` and `each_background` callbacks are removed. Use
  `each_example`.
* `-s` option for running particular scenarios is renamed to `-n`.
* Django-related functionality, including the `harvest` command, is moved to a
  separate project, [Aloe-Django][aloe-django].
* `terrain.py` has no particular significance. It will be imported but only if
  it exists at the same directory with the other step definition files, and not
  above it.

TODO
====

In no particular order:

* Feature and scenario tags should be converted to Nose tags.
* Verbose output (all steps printed as they run) is missing.

License
=======

Aloe - Cucumber runner for Python based on Lettuce and Nose
Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

[gherkin]: https://cucumber.io/
[nose]: https://nose.readthedocs.org/
[lettuce]: http://lettuce.it/
[gherkin-syntax]: https://cucumber.io/docs/reference
[aloe-django]: https://github.com/koterpillar/aloe_django
