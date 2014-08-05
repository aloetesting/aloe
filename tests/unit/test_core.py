# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
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

from inspect import currentframe

from lettuce import core
from sure import expect
from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.exc import SkipTest

from .test_step_parsing import parse_steps


STEP_WITH_TABLE = u'''
Given I have the following items in my shelf:
  | name  | description                                           |
  | Glass | a nice glass to drink grape juice                     |
  | Pasta | a pasta to cook and eat with grape juice in the glass |
  | Pasta | a pasta to cook and eat with grape juice in the glass |
'''


def test_step_definition():
    """
    Step definition takes a function and a step, keeps its definition
    relative path, and line + 1 (to consider the decorator)
    """

    line = currentframe().f_lineno
    def dumb():
        pass

    definition = core.StepDefinition("FOO BAR", dumb)
    assert_equals(definition.function, dumb)
    assert_equals(definition.file, core.fs.relpath(__file__).rstrip("c"))
    assert_equals(definition.line, line + 2)


def test_step_represented():
    """Step.represent_string behaviour when not defined"""

    class FakeFeature:
        max_length = 10

        class described_at:
            file = __file__

    class FakeScenario:
        feature = FakeFeature

    step, = core.Step.parse_steps_from_string('Given some sentence')
    step.scenario = FakeScenario

    assert_equals(
        step.represented(),
        u"    Given some sentence# %s:1" % __file__,
    )


def test_step_represent_table():
    """
    Step.represent_hashes
    """

    step, = parse_steps(STEP_WITH_TABLE)

    assert_equals(
        step.represent_hashes(), unicode(
        '      | name  | description                                           |\n'
        '      | Glass | a nice glass to drink grape juice                     |\n'
        '      | Pasta | a pasta to cook and eat with grape juice in the glass |\n'
        '      | Pasta | a pasta to cook and eat with grape juice in the glass |'
    ))

STEP_WITH_MATRIX = u'''
    Given i have the following matrix:
    | a  | b | ab |
    | 2 | 24 | 3 |
    '''

STEP_WITH_MATRIX2 = u'''
    Given i have the following matrix:
    | a  | a |
    | 2 | a |
    |  | 67 |
    '''

def test_step_represent_matrix():
    "Step with a more suggestive representation for a matrix"

    step, = parse_steps(STEP_WITH_MATRIX2)
    assert_equals(
        step.represent_hashes(),
    '      | a | a  |\n'
    '      | 2 | a  |\n'
    '      |   | 67 |'
    )

SCENARIO_OUTLINE = u'''
Scenario: Regular numbers
                               Given I do fill description with '<value_one>'
                               And then, age with with '<and_other>'
Examples:
         |     value_one       | and_other                   |
         | first| primeiro |
         |second |segundo|
'''


def test_scenario_outline_represent_examples():
    "Step.represent_hashes"

    raise SkipTest("not implemented")

    step = core.Scenario.from_string(SCENARIO_OUTLINE)

    assert_equals(
        step.represent_examples(),
        '    | value_one | and_other |\n'
        '    | first     | primeiro  |\n'
        '    | second    | segundo   |\n'
    )
