# -*- coding: utf-8 -*-
"""
Test parsing scenarios.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import zip
# pylint:enable=redefined-builtin

from unittest import skip

from aloe.parser import Step, Scenario, Feature
from aloe.exceptions import AloeSyntaxError

from nose.tools import assert_equal
from nose.tools import assert_raises


SCENARIO1 = """
Scenario: Adding some students to my university database
    Given I have the following courses in my university:
       | Name               | Duration |
       | Computer Science   | 5 years  |
       | Nutrition          | 4 years  |
    When I consolidate the database into 'courses.txt'
    Then I see the 1st line of 'courses.txt' has 'Computer Science:5'
    And I see the 2nd line of 'courses.txt' has 'Nutrition:4'
"""

OUTLINED_SCENARIO = """
Scenario Outline: Add two numbers
    Given I have entered <input_1> into the calculator
    And I have entered <input_2> into the calculator
    When I press <button>
    Then the result should be <output> on the screen

    Examples:
      | input_1 | input_2 | button | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |
"""

OUTLINED_SCENARIO_WITH_SUBSTITUTIONS_IN_TABLE = """
Scenario Outline: Bad configuration should fail
    Given I provide the following configuration:
       | Parameter | Value |
       |     a     |  <a>  |
       |     b     |  <b>  |
    When I run the program
    Then it should fail hard-core

Examples:
    | a | b |
    | 1 | 2 |
    | 2 | 4 |
"""

OUTLINED_SCENARIO_WITH_SUBSTITUTIONS_IN_MULTILINE = '''
Scenario Outline: Parsing HTML
    When I parse the HTML:
        """
        <div><v></div>
        """
    Then I should see "outline value"

Examples:
    | v             |
    | outline value |
'''

OUTLINED_FEATURE = """
    Feature: Do many things at once
        In order to automate tests
        As a automation freaky
        I want to use scenario outlines

        Scenario Outline: Add two numbers wisely
            Given I have entered <input_1> into the calculator
            And I have entered <input_2> into the calculator
            When I press <button>
            Then the result should be <output> on the screen

        Examples:
            | input_1 | input_2 | button | output |
            | 20      | 30      | add    | 50     |
            | 2       | 5       | add    | 7      |
            | 0       | 40      | add    | 40     |
"""

OUTLINED_FEATURE_WITH_MANY = """
    Feature: Full-featured feature
        Scenario Outline: Do something
            Given I have entered <input_1> into the <input_2>

        Examples:
            | input_1 | input_2 |
            | ok      | fail    |
            | fail    | ok      |

        Scenario: Do something else
          Given I am fine

        Scenario: Worked!
          Given it works
          When I look for something
          Then I find it

        Scenario Outline: Add two numbers wisely
            Given I have entered <input_1> into the calculator
            And I have entered <input_2> into the calculator
            When I press <button>
            Then the result should be <output> on the screen

        Examples:
            | input_1 | input_2 | button | output |
            | 20      | 30      | add    | 50     |
            | 2       | 5       | add    | 7      |
            | 0       | 40      | add    | 40     |

        Examples:
            | input_1 | input_2 | button | output |
            | 5       | 7       | add    | 12     |

"""

SCENARIO_FAILED = """
Scenario: Adding some students to my university database
       | Name               | Duration |
       | Computer Science   | 5 years  |
       | Nutrition          | 4 years  |
    When I consolidate the database into 'courses.txt'
    Then I see the 1st line of 'courses.txt' has 'Computer Science:5'
    And I see the 2nd line of 'courses.txt' has 'Nutrition:4'
"""

OUTLINED_SCENARIO_WITH_COMMENTS_ON_EXAMPLES = """
Scenario Outline: Add two numbers
    Given I have entered <input_1> into the calculator
    And I have entered <input_2> into the calculator
    When I press <button>
    Then the result should be <output> on the screen

    Examples:
      | input_1 | input_2 | button | output |
      | 20      | 30      | add    | 50     |
      #| 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |
    # end of the scenario
"""

OUTLINED_SCENARIO_WITH_MORE_THAN_ONE_EXAMPLES_BLOCK = """
Scenario Outline: Add two numbers
    Given I have entered <input_1> into the calculator
    And I have entered <input_2> into the calculator
    When I press <button>
    Then the result should be <output> on the screen

    Examples:
      | input_1 | input_2 | button | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |

    Examples:
      | input_1 | input_2 | button | output |
      | 20      | 33      | add    | 53     |
      | 12      | 40      | add    | 52     |
"""

COMMENTED_SCENARIO = """
Scenario: Adding some students to my university database
    Given I have the following courses in my university:
       | Name               | Duration |
       | Computer Science   | 5 years  |
       | Nutrition          | 4 years  |
    When I consolidate the database into 'courses.txt'
    Then I see the 1st line of 'courses.txt' has 'Computer Science:5'
    And I see the 2nd line of 'courses.txt' has 'Nutrition:4'

# Scenario: Adding some students to my university database
#     Given I have the following courses in my university:
#        | Name               | Duration |
#        | Computer Science   | 5 years  |
#        | Nutrition          | 4 years  |
#     When I consolidate the database into 'courses.txt'
#     Then I see the 1st line of 'courses.txt' has 'Computer Science:5'
#     And I see the 2nd line of 'courses.txt' has 'Nutrition:4'

"""

INLINE_COMMENTS_IGNORED_WITHIN_DOUBLE_QUOTES = '''
Scenario: Tweeting
  Given I am logged in on twitter
  When I search for the hashtag "#hammer"
'''

INLINE_COMMENTS_IGNORED_WITHIN_SINGLE_QUOTES = """
Scenario: Tweeting
  Given I am logged in on twitter
  When I search for the hashtag '#hammer'
"""


def parse_scenario(scenario, tags=None):
    """Parse a scenario, adding a feature header and tags."""
    feature_str = """
    Feature: test scenario
    """

    if tags:
        feature_str += ' '.join('@%s' % tag for tag in tags)

    feature_str += scenario

    feature = Feature.from_string(feature_str)

    return feature.scenarios[0]


def solved_steps(scenario):
    """A list of all the outline steps for a scenario."""

    return tuple(
        step
        for _, steps in scenario.evaluated
        for step in steps
    )


def test_scenario_has_name():
    """
    It should extract the name of the scenario
    """

    scenario = parse_scenario(SCENARIO1)

    assert isinstance(scenario, Scenario)

    assert_equal(
        scenario.name,
        "Adding some students to my university database"
    )


def test_scenario_has_repr():
    """
    Scenario implements __repr__ nicely
    """

    scenario = parse_scenario(SCENARIO1)
    assert_equal(
        repr(scenario),
        '<Scenario: "Adding some students to my university database">'
    )


def test_scenario_has_steps():
    """
    A scenario object should have a list of steps
    """

    scenario = parse_scenario(SCENARIO1)

    assert_equal(type(scenario.steps), tuple)
    assert_equal(len(scenario.steps), 4, "It should have 4 steps")

    expected_sentences = [
        "Given I have the following courses in my university:",
        "When I consolidate the database into 'courses.txt'",
        "Then I see the 1st line of 'courses.txt' has 'Computer Science:5'",
        "And I see the 2nd line of 'courses.txt' has 'Nutrition:4'",
    ]

    for step, expected_sentence in zip(scenario.steps, expected_sentences):
        assert_equal(type(step), Step)
        assert_equal(step.sentence, expected_sentence)

    assert_equal(scenario.steps[0].keys, ('Name', 'Duration'))
    assert_equal(
        scenario.steps[0].hashes,
        (
            {'Name': 'Computer Science', 'Duration': '5 years'},
            {'Name': 'Nutrition', 'Duration': '4 years'},
        )
    )


def test_scenario_may_own_outlines():
    """
    A scenario may own outlines
    """

    scenario = parse_scenario(OUTLINED_SCENARIO)

    assert_equal(len(scenario.steps), 4)
    expected_sentences = [
        'Given I have entered <input_1> into the calculator',
        'And I have entered <input_2> into the calculator',
        'When I press <button>',
        'Then the result should be <output> on the screen',
    ]

    for step, expected_sentence in zip(scenario.steps, expected_sentences):
        assert_equal(type(step), Step)
        assert_equal(step.sentence, expected_sentence)

    assert_equal(scenario.name, "Add two numbers")
    assert_equal(
        scenario.outlines,
        (
            {'input_1': '20', 'input_2': '30',
             'button': 'add', 'output': '50'},
            {'input_1': '2', 'input_2': '5',
             'button': 'add', 'output': '7'},
            {'input_1': '0', 'input_2': '40',
             'button': 'add', 'output': '40'},
        )
    )


def test_steps_parsed_by_scenarios_has_scenarios():
    """
    Steps parsed by scenarios has scenarios
    """

    scenario = parse_scenario(SCENARIO1)
    for step in scenario.steps:
        assert_equal(step.scenario, scenario)


def test_scenario_sentences_can_be_solved():
    """
    A scenario with outlines may solve its sentences
    """
    scenario = parse_scenario(OUTLINED_SCENARIO)
    solved = solved_steps(scenario)

    assert_equal(len(solved), 12)
    expected_sentences = [
        'Given I have entered 20 into the calculator',
        'And I have entered 30 into the calculator',
        'When I press add',
        'Then the result should be 50 on the screen',
        'Given I have entered 2 into the calculator',
        'And I have entered 5 into the calculator',
        'When I press add',
        'Then the result should be 7 on the screen',
        'Given I have entered 0 into the calculator',
        'And I have entered 40 into the calculator',
        'When I press add',
        'Then the result should be 40 on the screen',
    ]

    for step, expected in zip(solved, expected_sentences):
        assert_equal(type(step), Step)
        assert_equal(step.sentence, expected)


def test_scenario_tables_are_solved_against_outlines():
    """
    Outline substitution should apply to tables within a scenario
    """

    expected_hashes_per_step = [
        # a = 1, b = 2
        ({'Parameter': 'a', 'Value': '1'},
         {'Parameter': 'b', 'Value': '2'}),  # Given ...
        (),  # When I run the program
        (),  # Then I crash hard-core

        # a = 2, b = 4
        ({'Parameter': 'a', 'Value': '2'},
         {'Parameter': 'b', 'Value': '4'}),
        (),
        ()
    ]

    scenario = parse_scenario(OUTLINED_SCENARIO_WITH_SUBSTITUTIONS_IN_TABLE)
    solved = solved_steps(scenario)
    for step, expected in zip(solved, expected_hashes_per_step):
        assert_equal(type(step), Step)
        assert_equal(step.hashes, expected)


def test_scenario_multilines_are_solved_against_outlines():
    """
    Outline substitution should apply to multiline strings within a scenario
    """

    expected_multiline = '<div>outline value</div>'

    scenario = parse_scenario(
        OUTLINED_SCENARIO_WITH_SUBSTITUTIONS_IN_MULTILINE)
    step = solved_steps(scenario)[0]

    assert_equal(type(step), Step)
    assert_equal(step.multiline, expected_multiline)


def test_solved_steps_also_have_scenario_as_attribute():
    """
    Steps solved in scenario outlines also have scenario as attribute
    """

    scenario = parse_scenario(OUTLINED_SCENARIO)
    for step in solved_steps(scenario):
        assert_equal(step.scenario, scenario)


def test_scenario_outlines_within_feature():
    """
    Solving scenario outlines within a feature
    """

    feature = Feature.from_string(OUTLINED_FEATURE)
    scenario = feature.scenarios[0]
    solved = solved_steps(scenario)

    assert_equal(len(solved), 12)
    expected_sentences = [
        'Given I have entered 20 into the calculator',
        'And I have entered 30 into the calculator',
        'When I press add',
        'Then the result should be 50 on the screen',
        'Given I have entered 2 into the calculator',
        'And I have entered 5 into the calculator',
        'When I press add',
        'Then the result should be 7 on the screen',
        'Given I have entered 0 into the calculator',
        'And I have entered 40 into the calculator',
        'When I press add',
        'Then the result should be 40 on the screen',
    ]

    for step, expected in zip(solved, expected_sentences):
        assert_equal(type(step), Step)
        assert_equal(step.sentence, expected)


def test_full_featured_feature():
    """
    Solving scenarios within a full-featured feature
    """

    feature = Feature.from_string(OUTLINED_FEATURE_WITH_MANY)
    scenario1, scenario2, scenario3, scenario4 = feature.scenarios

    assert_equal(scenario1.name, 'Do something')
    assert_equal(scenario2.name, 'Do something else')
    assert_equal(scenario3.name, 'Worked!')
    assert_equal(scenario4.name, 'Add two numbers wisely')

    solved = solved_steps(scenario1)

    assert_equal(len(solved), 2)
    expected_sentences = [
        'Given I have entered ok into the fail',
        'Given I have entered fail into the ok',
    ]
    for step, expected in zip(solved, expected_sentences):
        assert_equal(step.sentence, expected)

    expected_evaluated = (
        (
            {'button': 'add', 'input_1': '20',
             'input_2': '30', 'output': '50'},
            [
                'Given I have entered 20 into the calculator',
                'And I have entered 30 into the calculator',
                'When I press add',
                'Then the result should be 50 on the screen',
            ]
        ),
        (
            {'button': 'add', 'input_1': '2',
             'input_2': '5', 'output': '7'},
            [
                'Given I have entered 2 into the calculator',
                'And I have entered 5 into the calculator',
                'When I press add',
                'Then the result should be 7 on the screen',
            ]
        ),
        (
            {'button': 'add', 'input_1': '0',
             'input_2': '40', 'output': '40'},
            [
                'Given I have entered 0 into the calculator',
                'And I have entered 40 into the calculator',
                'When I press add',
                'Then the result should be 40 on the screen',
            ],
        ),
        (
            {'button': 'add', 'input_1': '5',
             'input_2': '7', 'output': '12'},
            [
                'Given I have entered 5 into the calculator',
                'And I have entered 7 into the calculator',
                'When I press add',
                'Then the result should be 12 on the screen',
            ],
        )
    )
    for ((got_examples, got_steps), (expected_examples, expected_steps)) \
            in zip(scenario4.evaluated, expected_evaluated):
        assert_equal(got_examples, expected_examples)
        assert_equal([x.sentence for x in got_steps],
                     expected_steps)


@skip("FIXME: Gherkin parser allows this")
def test_scenario_with_table_and_no_step_fails():
    "A step table imediately after the scenario line, without step line fails"

    with assert_raises(AloeSyntaxError):
        parse_scenario(SCENARIO_FAILED)


def test_scenario_ignore_commented_lines_from_examples():
    "Comments on scenario example should be ignored"
    scenario = parse_scenario(OUTLINED_SCENARIO_WITH_COMMENTS_ON_EXAMPLES)

    assert_equal(
        scenario.outlines,
        (
            {'input_1': '20', 'input_2': '30',
             'button': 'add', 'output': '50'},
            {'input_1': '0', 'input_2': '40',
             'button': 'add', 'output': '40'},
        )
    )


def test_scenario_aggregate_all_examples_blocks():
    "All scenario's examples block should be translated to outlines"
    scenario = parse_scenario(
        OUTLINED_SCENARIO_WITH_MORE_THAN_ONE_EXAMPLES_BLOCK)

    assert_equal(
        scenario.outlines,
        (
            {'input_1': '20', 'input_2': '30',
             'button': 'add', 'output': '50'},
            {'input_1': '2', 'input_2': '5',
             'button': 'add', 'output': '7'},
            {'input_1': '0', 'input_2': '40',
             'button': 'add', 'output': '40'},
            {'input_1': '20', 'input_2': '33',
             'button': 'add', 'output': '53'},
            {'input_1': '12', 'input_2': '40',
             'button': 'add', 'output': '52'},
        )
    )


def test_commented_scenarios():
    "A scenario string that contains lines starting with '#' will be commented"
    scenario = parse_scenario(COMMENTED_SCENARIO)
    assert_equal(scenario.name,
                 'Adding some students to my university database')
    assert_equal(len(scenario.steps), 4)


def test_scenario_with_hash_within_double_quotes():
    ("Scenarios have hashes within double quotes and yet don't "
     "consider them as comments")

    scenario = parse_scenario(
        INLINE_COMMENTS_IGNORED_WITHIN_DOUBLE_QUOTES)

    step1, step2 = scenario.steps

    assert step1.sentence == u'Given I am logged in on twitter'
    assert step2.sentence == u'When I search for the hashtag "#hammer"'


def test_scenario_with_hash_within_single_quotes():
    ("Scenarios have hashes within single quotes and yet don't "
     "consider them as comments")

    scenario = parse_scenario(
        INLINE_COMMENTS_IGNORED_WITHIN_SINGLE_QUOTES)

    step1, step2 = scenario.steps

    assert step1.sentence == u'Given I am logged in on twitter'
    assert step2.sentence == u"When I search for the hashtag '#hammer'"
