# -*- coding: utf-8 -*-
"""
Steps for testing the basic Gherkin test functionality.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from aloe import after, before, step, world

# pylint:disable=unused-argument


@before.all
def init_all_results():
    """Initialise the result storage."""
    world.all_results = []


@before.each_example
def clear(*args):
    """Clean the results for each example."""
    world.numbers = []
    world.result = 0


@step(r'I have entered (\d+) into the calculator')
@step(r'我输入(\d+)')
def enter_number(self, number):
    """Store the entered number."""
    world.numbers.append(float(number))


@step(r'I press add')
@step(r'我按添加')
def press_add(self):
    """Sum up the numbers."""
    world.result = sum(world.numbers)


@step(r'I press \[\+\]')
def press_plus(self):
    """
    Alias of 'I press add'.

    Tests behave_as().
    """
    self.given('I press add')


@step(r'I have a table')
def have_table(self):
    """Nothing."""


@step(r'The result should be (\d+) on the screen')
@step(r'结果应该是(\d+)')
def assert_result(self, result):
    """Assert the result is correct."""
    assert world.result == float(result)


@after.each_example
def record_all_results(scenario, outline, steps):
    """
    Record all results for the example
    """

    world.all_results.append(world.result)
