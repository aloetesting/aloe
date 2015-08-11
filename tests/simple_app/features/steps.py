# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
def enter_number(self, number):
    """Store the entered number."""
    world.numbers.append(float(number))


@step(r'I press add')
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
def assert_result(self, result):
    """Assert the result is correct."""
    assert world.result == float(result)


@after.each_example
def record_all_results(scenario, outline, steps):
    """
    Record all results for the example
    """

    world.all_results.append(world.result)
