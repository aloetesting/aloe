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

I_LIKE_VEGETABLES = '''
Given I hold a special love for green vegetables
'''

I_HAVE_TASTY_BEVERAGES = '''
Given I have the following tasty beverages in my freezer:
   | Name   | Type     | Price |
   | Skol   | Beer     |  3.80 |
   | Nestea | Ice-tea  |  2.10 |
'''

I_DIE_HAPPY = '''
Given I shall die with love in my heart
'''

BACKGROUND_WITH_TAGGED_SCENARIO = '''
    Background:
        background line 1

    @wip
    Scenario:
        Scenario line 1
'''

MULTI_LINE = '''
Given I have a string like so:
  """
  This is line one
  and this is line two
  and this is line three
    and this is line four,

    with spaces at the beginning
  """
'''.strip()

MULTI_LINE_WHITESPACE = '''
Given I have a string like so:
  """
  This is line one
  and this is line two
  and this is line three
 "  and this is line four,
 "
 "  with spaces at the beginning
  and spaces at the end   "
  """
'''.strip()


INVALID_MULTI_LINE = '''
  """
  invalid one...
  """
'''.strip()

import string
from lettuce.parser import Feature, Step
from lettuce.exceptions import LettuceSyntaxError
from lettuce import strings
from nose.tools import assert_equals, assert_raises
from nose.exc import SkipTest
from tests.asserts import *


def parse_steps(step):
    feature = """
    Feature: parse a step
    Scenario: parse a single step
    """

    feature += step

    return Feature.from_string(feature).scenarios[0].steps


def first_line_of(step):
    """
    Return the first line of a step
    """
    return step.strip().splitlines()[0]


def test_step_has_repr():
    """
    Step implements __repr__ nicely
    """
    step, = parse_steps(I_HAVE_TASTY_BEVERAGES)
    assert_equals(
        repr(step),
        '<Step: "' + first_line_of(I_HAVE_TASTY_BEVERAGES) + '">'
    )


def test_can_get_sentence_from_string():
    """
    It should extract the sentence string from the whole step
    """

    step, = parse_steps(I_HAVE_TASTY_BEVERAGES)

    assert isinstance(step, Step)

    assert_equals(
        step.sentence,
        first_line_of(I_HAVE_TASTY_BEVERAGES)
    )


def test_can_parse_keys_from_table():
    """
    It should take the keys from the step, if it has a table
    """

    step, = parse_steps(I_HAVE_TASTY_BEVERAGES)
    assert_equals(step.keys, ('Name', 'Type', 'Price'))


def test_can_parse_tables():
    """
    It should have a list of data from a given step, if it has a table
    """

    step, = parse_steps(I_HAVE_TASTY_BEVERAGES)

    assert isinstance(step.hashes, list)
    assert_equals(len(step.hashes), 2)
    assert_equals(
        step.hashes[0],
        {
            'Name': 'Skol',
            'Type': 'Beer',
            'Price': '3.80'
        }
    )
    assert_equals(
        step.hashes[1],
        {
            'Name': 'Nestea',
            'Type': 'Ice-tea',
            'Price': '2.10'
        }
    )


def test_can_parse_a_unary_array_from_single_step():
    """
    It should extract a single ordinary step correctly into an array of steps
    """

    steps = parse_steps(I_HAVE_TASTY_BEVERAGES)
    assert_equals(len(steps), 1)
    assert isinstance(steps[0], Step)
    assert_equals(steps[0].sentence,
                  first_line_of(I_HAVE_TASTY_BEVERAGES))


def test_can_parse_a_unary_array_from_complicated_step():
    """
    It should extract a single tabular step correctly into an array of steps
    """

    steps = parse_steps(I_LIKE_VEGETABLES)
    assert_equals(len(steps), 1)
    assert isinstance(steps[0], Step)
    assert_equals(steps[0].sentence, first_line_of(I_LIKE_VEGETABLES))


def test_can_parse_regular_step_followed_by_tabular_step():
    """
    It should correctly extract two steps (one regular, one tabular) into an
    array.
    """
    steps = parse_steps(I_LIKE_VEGETABLES + I_HAVE_TASTY_BEVERAGES)
    assert_equals(len(steps), 2)
    assert isinstance(steps[0], Step)
    assert isinstance(steps[1], Step)
    assert_equals(steps[0].sentence, first_line_of(I_LIKE_VEGETABLES))
    assert_equals(steps[1].sentence, first_line_of(I_HAVE_TASTY_BEVERAGES))


def test_can_parse_tabular_step_followed_by_regular_step():
    """"
    It should correctly extract two steps (one tabular, one regular) into
    an array.
    """

    steps = parse_steps(I_HAVE_TASTY_BEVERAGES + I_LIKE_VEGETABLES)
    assert_equals(len(steps), 2)
    assert isinstance(steps[0], Step)
    assert isinstance(steps[1], Step)
    assert_equals(steps[0].sentence, first_line_of(I_HAVE_TASTY_BEVERAGES))
    assert_equals(steps[1].sentence, first_line_of(I_LIKE_VEGETABLES))


def test_can_parse_two_ordinary_steps():
    """
    It should correctly extract two ordinary steps into an array.
    """

    steps = parse_steps(I_DIE_HAPPY + I_LIKE_VEGETABLES)
    assert_equals(len(steps), 2)
    assert isinstance(steps[0], Step)
    assert isinstance(steps[1], Step)
    assert_equals(steps[0].sentence, first_line_of(I_DIE_HAPPY))
    assert_equals(steps[1].sentence, first_line_of(I_LIKE_VEGETABLES))


def test_cannot_start_with_multiline():
    """
    It should raise an error when a step starts with a multiline string
    """

    with assert_raises(LettuceSyntaxError):
        step = parse_steps(INVALID_MULTI_LINE)


def test_multiline_is_part_of_previous_step():
    """
    It should correctly parse a multi-line string as part of the preceding step
    """

    steps = parse_steps(MULTI_LINE)
    assert_equals(len(steps), 1)
    assert isinstance(steps[0], Step)
    assert_equals(steps[0].sentence, 'Given I have a string like so:')


def test_table_escaping():
    """
    Table columns can be correctly escaped
    """

    STEPS = """
    Given I have items in my table:
        | Column 1                 |
        | This is a column         |
        | This is \| also a column |
    """

    steps = parse_steps(STEPS)

    assert_equals(len(steps), 1)

    step, = steps

    assert_equals(step.table, [
        ['Column 1'],
        ['This is a column'],
        ['This is | also a column'],
    ])


# FIXME: I want to have a discussion on what is correct in Gherkin before
# making the parser work this way
def test_multiline_is_parsed():
    raise SkipTest("multiline")
    step, = parse_steps(MULTI_LINE)
    assert_equals(step.sentence, 'Given I have a string like so:')
    assert_equals(step.multiline, u"""This is line one
and this is line two
and this is line three
and this is line four,
with spaces at the beginning""")


def test_multiline_with_whitespace():
    raise SkipTest("multiline")
    step, = parse_steps(MULTI_LINE_WHITESPACE)
    assert_equals(step.sentence, 'I have a string like so:')
    assert_equals(step.multiline, u"""This is line one
and this is line two
and this is line three
  and this is line four,

  with spaces at the beginning
and spaces at the end   """)
