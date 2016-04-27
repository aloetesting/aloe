# -*- coding: utf-8 -*-
"""
Test parsing steps.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest

from aloe.parser import Feature, Step


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


def parse_steps(step):
    """Parse a step, prefixing it with a feature and a scenario header."""
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


class TestStepParsing(unittest.TestCase):
    """Test parsing steps."""

    def test_step_has_repr(self):
        """
        Step implements __repr__ nicely
        """
        step, = parse_steps(I_HAVE_TASTY_BEVERAGES)
        self.assertEqual(
            repr(step),
            '<Step: "' + first_line_of(I_HAVE_TASTY_BEVERAGES) + '">'
        )

    def test_can_get_sentence_from_string(self):
        """
        It should extract the sentence string from the whole step
        """

        step, = parse_steps(I_HAVE_TASTY_BEVERAGES)

        assert isinstance(step, Step)

        self.assertEqual(
            step.sentence,
            first_line_of(I_HAVE_TASTY_BEVERAGES)
        )

    def test_can_parse_keys_from_table(self):
        """
        It should take the keys from the step, if it has a table
        """

        step, = parse_steps(I_HAVE_TASTY_BEVERAGES)
        self.assertEqual(step.keys, ('Name', 'Type', 'Price'))

    def test_can_parse_tables(self):
        """
        It should have a list of data from a given step, if it has a table
        """

        step, = parse_steps(I_HAVE_TASTY_BEVERAGES)

        self.assertEqual(step.hashes, (
            {
                'Name': 'Skol',
                'Type': 'Beer',
                'Price': '3.80'
            },
            {
                'Name': 'Nestea',
                'Type': 'Ice-tea',
                'Price': '2.10'
            },
        ))

    def test_can_parse_a_unary_array_from_single_step(self):
        """
        It should extract a single ordinary step correctly into an array of
        steps
        """

        steps = parse_steps(I_HAVE_TASTY_BEVERAGES)
        self.assertEqual(len(steps), 1)
        assert isinstance(steps[0], Step)
        self.assertEqual(steps[0].sentence,
                         first_line_of(I_HAVE_TASTY_BEVERAGES))

    def test_can_parse_a_unary_array_from_complicated_step(self):
        """Test extracting a single tabular step into an array of steps."""

        steps = parse_steps(I_LIKE_VEGETABLES)
        self.assertEqual(len(steps), 1)
        assert isinstance(steps[0], Step)
        self.assertEqual(steps[0].sentence, first_line_of(I_LIKE_VEGETABLES))

    def test_can_parse_regular_step_followed_by_tabular_step(self):
        """
        Test extracting two steps (one regular, one tabular) into an array.
        """
        steps = parse_steps(I_LIKE_VEGETABLES + I_HAVE_TASTY_BEVERAGES)
        self.assertEqual(len(steps), 2)
        assert isinstance(steps[0], Step)
        assert isinstance(steps[1], Step)
        self.assertEqual(steps[0].sentence, first_line_of(I_LIKE_VEGETABLES))
        self.assertEqual(steps[1].sentence,
                         first_line_of(I_HAVE_TASTY_BEVERAGES))

    def test_can_parse_tabular_step_followed_by_regular_step(self):
        """
        Test extracting two steps (one tabular, one regular) into an array.
        """

        steps = parse_steps(I_HAVE_TASTY_BEVERAGES + I_LIKE_VEGETABLES)
        self.assertEqual(len(steps), 2)
        assert isinstance(steps[0], Step)
        assert isinstance(steps[1], Step)
        self.assertEqual(steps[0].sentence,
                         first_line_of(I_HAVE_TASTY_BEVERAGES))
        self.assertEqual(steps[1].sentence, first_line_of(I_LIKE_VEGETABLES))

    def test_can_parse_two_ordinary_steps(self):
        """
        It should correctly extract two ordinary steps into an array.
        """

        steps = parse_steps(I_DIE_HAPPY + I_LIKE_VEGETABLES)
        self.assertEqual(len(steps), 2)
        assert isinstance(steps[0], Step)
        assert isinstance(steps[1], Step)
        self.assertEqual(steps[0].sentence, first_line_of(I_DIE_HAPPY))
        self.assertEqual(steps[1].sentence, first_line_of(I_LIKE_VEGETABLES))

    def test_multiline_is_part_of_previous_step(self):
        """
        It should correctly parse a multi-line string as part of the preceding
        step
        """

        steps = parse_steps(MULTI_LINE)
        self.assertEqual(len(steps), 1)
        assert isinstance(steps[0], Step)
        self.assertEqual(steps[0].sentence, 'Given I have a string like so:')

    def test_table_escaping(self):
        """
        Table columns can be correctly escaped
        """

        steps = parse_steps(r"""
        Given I have items in my table:
            | Column 1                 |
            | This is a column         |
            | This is \| also a column |
            | This is \\ a backslash   |
        """)

        self.assertEqual(len(steps), 1)

        step, = steps

        self.assertEqual(step.table, (
            (r'Column 1',),
            (r'This is a column',),
            (r'This is | also a column',),
            (r'This is \ a backslash',),
        ))

    def test_multiline_is_parsed(self):
        """Test parsing a multiline string in a step."""
        step, = parse_steps(MULTI_LINE)
        self.assertEqual(step.sentence, 'Given I have a string like so:')
        self.assertEqual(step.multiline, u"""This is line one
and this is line two
and this is line three
  and this is line four,

  with spaces at the beginning""")

    def test_step_with_hash(self):
        """Test parsing a step with a hash"""
        step, = parse_steps('''
        Given I have product #1234 in my cart
        ''')

        self.assertEqual(step.sentence, 'Given I have product #1234 in my cart')

    def test_comments(self):
        """Test parsing Gherkin comments."""
        steps = parse_steps('''
        # A comment
        Given I have a comment
                            # Another comment
        And I have another comment
        ''')

        self.assertEqual(
            [step.sentence for step in steps],
            [
                'Given I have a comment',
                'And I have another comment',
            ]
        )

    def test_multiline_with_hash(self):
        """Test parsing a multiline with a hash"""
        step, = parse_steps('''
        Given I have the following products in my cart:
        """
        #1234
        #2345
        """
        ''')

        self.assertEqual(step.multiline, u"#1234\n#2345")
