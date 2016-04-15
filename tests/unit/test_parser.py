# -*- coding: utf-8 -*-
"""
Test Gherkin parser.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import zip
# pylint:enable=redefined-builtin

import tempfile

from nose.tools import assert_equal, assert_raises

from aloe.parser import Feature, Scenario, Background
from aloe.exceptions import AloeSyntaxError

FEATURE1 = """
Feature: Rent movies
    Scenario: Renting a featured movie
        Given I have the following movies in my database
           | Name                    | Rating  | New | Available |
           | Matrix Revolutions      | 4 stars | no  | 6         |
           | Iron Man 2              | 5 stars | yes | 11        |
        When the client 'John Doe' rents 'Iron man 2'
        Then he needs to pay 10 bucks

    Scenario: Renting a non-featured movie
        Given I have the following movies in my database
           | Name                    | Rating  | New | Available |
           | A night at the museum 2 | 3 stars | yes | 9         |
           | Matrix Revolutions      | 4 stars | no  | 6         |
        When the client 'Mary Doe' rents 'Matrix Revolutions'
        Then she needs to pay 6 bucks

    Scenario: Renting two movies allows client to take one more without charge
        Given I have the following movies in my database
           | Name                    | Rating  | New | Available |
           | A night at the museum 2 | 3 stars | yes | 9         |
           | Matrix Revolutions      | 4 stars | no  | 6         |
           | Iron Man 2              | 5 stars | yes | 11        |
        When the client 'Jack' rents 'Iron man 2'
        And also rents 'Iron man 2' and 'A night at the museum 2'
        Then he needs to pay 16 bucks
"""

FEATURE2 = """
Feature: Division
      In order to avoid silly mistakes
      Cashiers must be able to calculate a fraction

      Scenario: Regular numbers
            Given I have entered 3 into the calculator
            And I have entered 2 into the calculator
            When I press divide
            Then the result should be 1.5 on the screen
"""

FEATURE3 = """
Feature: A long line as feature name will define the max length of the feature
  In order to describe my features
  I want to add description on them
  Scenario: Regular numbers
    Given nothing to do
"""

FEATURE4 = """
Feature: Big sentence
  As a clever guy
  I want to describe this Feature
  So that I can take care of my Scenario
  Scenario: Regular numbers
    Given a huge sentence, that have so many characters
    And another one, very tiny
"""

FEATURE5 = """
Feature: Big table
  Scenario: Regular numbers
    Given that I have these items:
      | description                                                               |
      | this is such a huge description within a table, the maxlengh will be huge |
      | this is another description within a table                                |
"""

FEATURE6 = """
Feature: Big scenario outline
  Scenario Outline: Regular numbers
    Given I do fill 'description' with '<value_two>'
  Examples:
    | value_two                                                               |
    | this is such a huge value within a table, the maxlengh will be damn big |
    | this is another description within a table                              |

"""

FEATURE7 = """
Feature: Big table
  Scenario: Regular numbers
    Given that I have these items:
      | description-long-as-hell | name-that-will-make-my-max-length-big |
      | one                      | john                                  |
      | two                      | baby                                  |
"""

FEATURE8 = """
Feature: Big scenario outline
  Scenario Outline: big scenario outlines
    Given I do fill 'description' with '<value_two>'

  Examples:
    | value_two_thousand_and_three | another_one | and_even_bigger |
    | 1                            | um          | one             |
    | 2                            | dois        | two             |
"""

FEATURE9 = """
Feature: Big scenario outline
  Scenario Outline: big scenario outlines
    Given I do fill 'description' with '<value_two>'

  Examples:
    | value_two_thousand_and_three_biiiiiiiiiiiiiiiiiiiiiiiiiiiiig |
    | 1                                                            |
    | 2                                                            |
    | 3                                                            |
"""

FEATURE10 = """
Feature: Big sentence
  As a clever guy
  I want to describe this Feature
  So that I can take care of my Scenario
  Scenario: Regular numbers
    Given a huge sentence, that have so many characters
    And another one, very tiny

    # Feature: Big sentence
    #   As a clever guy
    #   I want to describe this Feature
    #   So that I can take care of my Scenario
    #   Scenario: Regular numbers
    #     Given a huge sentence, that have so many characters
    #     And another one, very tiny
"""

FEATURE11 = """
Feature: Yay tags
  @many @other
  @basic
  @tags @here @:)
  Scenario: Double Yay
    Given this scenario has tags
    Then it can be inspected from within the object
"""

FEATURE12 = """
Feature: Yay tags and many scenarios
  @many @other
  @basic
  @tags @here @:)
  Scenario: Holy tag, Batman
    Given this scenario has tags
    Then it can be inspected from within the object

  @only
  @a-few @tags
  Scenario: Holy guacamole
    Given this scenario has tags
    Then it can be inspected from within the object

"""

FEATURE13 = '''
Feature: correct matching
  @runme
  Scenario: Holy tag, Batman
    Given this scenario has tags
    Then it can be inspected from within the object

  Scenario: This has no tags
    Given this scenario has no tags
    Then I fill my email with gabriel@lettuce.it

  @slow
  Scenario: this is slow
    Given this scenario has tags
    When I fill my email with "gabriel@lettuce.it"
    Then it can be inspected from within the object

  Scenario: Also without tags
    Given this scenario has no tags
    Then I fill my email with 'gabriel@lettuce.it'
'''

FEATURE14 = """
Feature:    Extra whitespace feature
  I want to match scenarios with extra whitespace
  Scenario:    Extra whitespace scenario
    Given this scenario, which has extra leading whitespace
    Then the scenario definition should still match
"""

FEATURE15 = """
Feature: Redis database server

    Scenario: Bootstraping Redis role
        Given I have a an empty running farm
        When I add redis role to this farm
        Then I expect server bootstrapping as M1
        And scalarizr version is last in M1
        And redis is running on M1

    Scenario: Restart scalarizr
        When I reboot scalarizr in M1
        And see 'Scalarizr terminated' in M1 log
        Then scalarizr process is 2 in M1
        And not ERROR in M1 scalarizr log

    @rebundle
    Scenario: Rebundle server
        When I create server snapshot for M1
        Then Bundle task created for M1
        And Bundle task becomes completed for M1

    @rebundle
    Scenario: Use new role
        Given I have a an empty running farm
        When I add to farm role created by last bundle task
        Then I expect server bootstrapping as M1

    @rebundle
    Scenario: Restart scalarizr after bundling
        When I reboot scalarizr in M1
        And see 'Scalarizr terminated' in M1 log
        Then scalarizr process is 2 in M1
        And not ERROR in M1 scalarizr log

    Scenario: Bundling data
        When I trigger databundle creation
        Then Scalr sends DbMsr_CreateDataBundle to M1
        And Scalr receives DbMsr_CreateDataBundleResult from M1
        And Last databundle date updated to current

    Scenario: Modifying data
        Given I have small-sized database 1 on M1
        When I create a databundle
        And I terminate server M1
        Then I expect server bootstrapping as M1
        And M1 contains database 1

    Scenario: Reboot server
        When I reboot server M1
        Then Scalr receives RebootStart from M1
        And Scalr receives RebootFinish from M1

    Scenario: Backuping data on Master
        When I trigger backup creation
        Then Scalr sends DbMsr_CreateBackup to M1
        And Scalr receives DbMsr_CreateBackupResult from M1
        And Last backup date updated to current

    Scenario: Setup replication
        When I increase minimum servers to 2 for redis role
        Then I expect server bootstrapping as M2
        And scalarizr version is last in M2
        And M2 is slave of M1

    Scenario: Restart scalarizr in slave
        When I reboot scalarizr in M2
        And see 'Scalarizr terminated' in M2 log
        Then scalarizr process is 2 in M2
        And not ERROR in M2 scalarizr log

    Scenario: Slave force termination
        When I force terminate M2
        Then Scalr sends HostDown to M1
        And not ERROR in M1 scalarizr log
        And redis is running on M1
        And scalarizr process is 2 in M1
        Then I expect server bootstrapping as M2
        And not ERROR in M1 scalarizr log
        And not ERROR in M2 scalarizr log
        And redis is running on M1

    @ec2
    Scenario: Slave delete EBS
        When I know M2 ebs storage
        And M2 ebs status is in-use
        Then I terminate server M2 with decrease
        And M2 ebs status is deleting
        And not ERROR in M1 scalarizr log

    @ec2
    Scenario: Setup replication for EBS test
        When I increase minimum servers to 2 for redis role
        Then I expect server bootstrapping as M2
        And M2 is slave of M1

    Scenario: Writing on Master, reading on Slave
        When I create database 2 on M1
        Then M2 contains database 2

    Scenario: Slave -> Master promotion
        Given I increase minimum servers to 3 for redis role
        And I expect server bootstrapping as M3
        When I create database 3 on M1
        And I terminate server M1 with decrease
        Then Scalr sends DbMsr_PromoteToMaster to N1
        And Scalr receives DbMsr_PromoteToMasterResult from N1
        And Scalr sends DbMsr_NewMasterUp to all
        And M2 contains database 3

    @restart_farm
    Scenario: Restart farm
        When I stop farm
        And wait all servers are terminated
        Then I start farm
        And I expect server bootstrapping as M1
        And scalarizr version is last in M1
        And redis is running on M1
        And M1 contains database 3
        Then I expect server bootstrapping as M2
        And M2 is slave of M1
        And M2 contains database 3
        """

FEATURE16 = """
Feature: Movie rental
    As a rental store owner
    I want to keep track of my clients
    So that I can manage my business better

    Background:
        Given I have the following movies in my database:
           | Name                    | Rating  | New | Available |
           | Matrix Revolutions      | 4 stars | no  | 6         |
           | Iron Man 2              | 5 stars | yes | 11        |
        And the following clients:
           | Name      |
           | John Doe  |
           | Foo Bar   |

    Scenario: Renting a featured movie
        Given the client 'John Doe' rents 'Iron Man 2'
        Then there are 10 more left

    Scenario: Renting an old movie
        Given the client 'Foo Bar' rents 'Matrix Revolutions'
        Then there are 5 more left
"""

FEATURE17 = """
Feature: Movie rental without MMF
    Background:
        Given I have the following movies in my database:
           | Name                    | Rating  | New | Available |
           | Matrix Revolutions      | 4 stars | no  | 6         |
           | Iron Man 2              | 5 stars | yes | 11        |
        And the following clients:
           | Name      |
           | John Doe  |
           | Foo Bar   |

    Scenario: Renting a featured movie
        Given the client 'John Doe' rents 'Iron Man 2'
        Then there are 10 more left
"""

FEATURE18 = """
@feature_runme
Feature: correct matching
  @runme1
  Scenario: Holy tag, Batman [1]
    Given this scenario has tags
    Then it can be inspected from within the object

  @runme2
  Scenario: Holy tag2, Batman (2)
    Given this scenario has other tags
    Then it can be inspected from within the object even with the table
    | What | Is | This  |
    | It   | is | TABLE |

  @runme3
  Scenario: Holy tag3, Batman
    Given this scenario has even more tags
    Then it can be inspected from within the object

"""

FEATURE19 = """
Feature: correct matching
  @runme1
  Scenario: Holy tag, Batman (1)
    Given this scenario has tags
    Then it can be inspected from within the object

  @runme2
  Scenario: Holy tag2, Batman [2]
    Given this scenario has other tags
    Then it can be inspected from within the object
"""

FEATURE20 = """
Feature: My scenarios have no name
    Scenario:
        Given this scenario raises a syntax error
"""

FEATURE21 = """
Feature: Taming the tag parser

  Background:
    Given the email addresses:
      | name         | email                      |
      | Chuck Norris | roundhouse@chucknorris.com |
    Then the next scenario has only the tags it's supposed to

  Scenario: I'm isolated
    Given I am parsed
    Then this scenario has only zero tags

  @tag
  Scenario: I'm so isolated
    Given I am parsed
    Then this scenario has one tag
"""

FEATURE22 = """
Feature: one tag in the first scenario

  @onetag
  Scenario: This is the first scenario
    Given I am parsed
    Then this scenario has one tag
"""

FEATURE23 = """
Feature: three tags in the first scenario

  @onetag @another @$%^&even-weird_chars
  Scenario: This is the first scenario
    Given I am parsed
    Then this scenario has three tags
"""


def test_feature_has_repr():
    """
    Feature implements __repr__ nicely
    """
    feature = Feature.from_string(FEATURE1)
    assert repr(feature) == '<Feature: "Rent movies">'


def test_scenario_has_name():
    """
    It should extract the name string from the scenario
    """

    feature = Feature.from_string(FEATURE1)

    assert isinstance(feature, Feature)

    assert feature.name == "Rent movies"


def test_feature_has_scenarios():
    """
    A feature object should have a list of scenarios
    """

    feature = Feature.from_string(FEATURE1)

    assert isinstance(feature.scenarios, tuple)
    assert len(feature.scenarios) == 3

    expected_names = [
        "Renting a featured movie",
        "Renting a non-featured movie",
        "Renting two movies allows client to take one more without charge",
    ]

    for scenario, expected_name in zip(feature.scenarios, expected_names):
        assert isinstance(scenario, Scenario)
        assert scenario.name == expected_name

    assert_equal(
        feature.scenarios[1].steps[0].keys,
        ('Name', 'Rating', 'New', 'Available')
    )

    assert list(feature.scenarios[1].steps[0].hashes) == [
        {
            'Name': 'A night at the museum 2',
            'Rating': '3 stars',
            'New': 'yes',
            'Available': '9',
        },
        {
            'Name': 'Matrix Revolutions',
            'Rating': '4 stars',
            'New': 'no',
            'Available': '6',
        },
    ]


def test_outline_steps():
    """Test steps that are part of an outline."""

    feature = Feature.from_string(FEATURE6)

    # Steps that are a part of an outline have a reference back to the outline
    for outline, steps in feature.scenarios[0].evaluated:
        for step in steps:
            assert_equal(step.outline, outline)

    feature = Feature.from_string(FEATURE1)

    # Steps that are not a part of an outline don't have the outline reference
    for outline, steps in feature.scenarios[0].evaluated:
        for step in steps:
            assert_equal(step, outline, None)


def test_can_parse_feature_description():
    """
    A feature object should have a description
    """

    feature = Feature.from_string(FEATURE2)

    assert_equal(
        feature.description,
        "In order to avoid silly mistakes\n"
        "Cashiers must be able to calculate a fraction"
    )
    expected_scenario_names = ["Regular numbers"]
    got_scenario_names = [s.name for s in feature.scenarios]

    assert_equal(expected_scenario_names, got_scenario_names)
    assert_equal(len(feature.scenarios[0].steps), 4)

    step1, step2, step3, step4 = feature.scenarios[0].steps

    assert_equal(step1.sentence, 'Given I have entered 3 into the calculator')
    assert_equal(step2.sentence, 'And I have entered 2 into the calculator')
    assert_equal(step3.sentence, 'When I press divide')
    assert_equal(step4.sentence,
                 'Then the result should be 1.5 on the screen')


def test_scenarios_parsed_by_feature_has_feature():
    "Scenarios parsed by features has feature"

    feature = Feature.from_string(FEATURE2)

    for scenario in feature.scenarios:
        assert_equal(scenario.feature, feature)


def test_feature_max_length_on_scenario():
    """
    The max length of a feature considering when the scenario is longer than
    the remaining things
    """

    feature = Feature.from_string(FEATURE1)
    assert_equal(feature.max_length, 76)


def test_feature_max_length_on_feature_description():
    """
    The max length of a feature considering when one of the description lines
    of the feature is longer than the remaining things
    """

    feature = Feature.from_string(FEATURE2)
    assert_equal(feature.max_length, 47)


def test_feature_max_length_on_feature_name():
    """
    The max length of a feature considering when the name of the feature
    is longer than the remaining things
    """

    feature = Feature.from_string(FEATURE3)
    assert_equal(feature.max_length, 78)


def test_feature_max_length_on_step_sentence():
    """
    The max length of a feature considering when the some of the step sentences
    is longer than the remaining things
    """

    feature = Feature.from_string(FEATURE4)
    assert_equal(feature.max_length, 55)


def test_feature_max_length_on_step_with_table():
    """
    The max length of a feature considering when the table of some of the steps
    is longer than the remaining things
    """

    feature = Feature.from_string(FEATURE5)
    assert_equal(feature.max_length, 83)


def test_feature_max_length_on_step_with_table_keys():
    """
    The max length of a feature considering when the table keys of some of the
    steps are longer than the remaining things
    """

    feature = Feature.from_string(FEATURE7)
    assert_equal(feature.max_length, 74)


def test_feature_max_length_on_scenario_outline():
    """
    The max length of a feature considering when the table of some of the
    scenario oulines is longer than the remaining things
    """

    feature = Feature.from_string(FEATURE6)
    assert_equal(feature.max_length, 79)


def test_feature_max_length_on_scenario_outline_keys():
    """
    The max length of a feature considering when the table keys of the
    scenario oulines are longer than the remaining things
    """

    feature1 = Feature.from_string(FEATURE8)
    feature2 = Feature.from_string(FEATURE9)
    assert_equal(feature1.max_length, 68)
    assert_equal(feature2.max_length, 68)


def test_description_on_long_named_feature():
    "Can parse the description on long named features"
    feature = Feature.from_string(FEATURE3)
    assert_equal(
        feature.description,
        "In order to describe my features\n"
        "I want to add description on them",
    )


def test_description_on_big_sentenced_steps():
    "Can parse the description on long sentenced steps"
    feature = Feature.from_string(FEATURE4)
    assert_equal(
        feature.description,
        "As a clever guy\n"
        "I want to describe this Feature\n"
        "So that I can take care of my Scenario",
    )


def test_comments():
    """
    It should ignore lines that start with #, despite white spaces
    """

    feature = Feature.from_string(FEATURE10)

    assert_equal(feature.max_length, 55)


def test_single_scenario_single_scenario():
    "Features should have at least the first scenario parsed with tags"
    feature = Feature.from_string(FEATURE11)

    first_scenario = feature.scenarios[0]

    assert_equal(first_scenario.tags, (
        'many', 'other', 'basic', 'tags', 'here', ':)'
    ))


def test_single_feature_single_tag():
    "All scenarios within a feature inherit the feature's tags"
    feature = Feature.from_string(FEATURE18)

    assert feature.scenarios[0].tags == ('runme1', 'feature_runme')

    assert feature.scenarios[1].tags == ('runme2', 'feature_runme')

    assert feature.scenarios[2].tags == ('runme3', 'feature_runme')


def test_single_scenario_many_scenarios():
    "Untagged scenario following a tagged one should have no tags"

    feature = Feature.from_string(FEATURE13)

    first_scenario = feature.scenarios[0]
    assert first_scenario.tags == ('runme',)

    second_scenario = feature.scenarios[1]
    assert second_scenario.tags == ()

    third_scenario = feature.scenarios[2]
    assert third_scenario.tags == ('slow',)

    last_scenario = feature.scenarios[3]
    assert last_scenario.tags == ()


def test_scenarios_with_extra_whitespace():
    "Make sure that extra leading whitespace is ignored"
    feature = Feature.from_string(FEATURE14)

    assert_equal(type(feature.scenarios), tuple)
    assert_equal(len(feature.scenarios), 1, "It should have 1 scenario")
    assert_equal(feature.name, "Extra whitespace feature")

    scenario = feature.scenarios[0]
    assert_equal(type(scenario), Scenario)
    assert_equal(scenario.name, "Extra whitespace scenario")


def test_scenarios_parsing():
    "Tags are parsed correctly"
    feature = Feature.from_string(FEATURE15)
    scenarios_and_tags = [(s.name, s.tags) for s in feature.scenarios]

    assert_equal(scenarios_and_tags, [
        ('Bootstraping Redis role', ()),
        ('Restart scalarizr', ()),
        ('Rebundle server', ('rebundle',)),
        ('Use new role', ('rebundle',)),
        ('Restart scalarizr after bundling', ('rebundle',)),
        ('Bundling data', ()),
        ('Modifying data', ()),
        ('Reboot server', ()),
        ('Backuping data on Master', ()),
        ('Setup replication', ()),
        ('Restart scalarizr in slave', ()),
        ('Slave force termination', ()),
        ('Slave delete EBS', ('ec2',)),
        ('Setup replication for EBS test', ('ec2',)),
        ('Writing on Master, reading on Slave', ()),
        ('Slave -> Master promotion', ()),
        ('Restart farm', ('restart_farm',)),
    ])


def test_scenarios_with_special_characters():
    "Make sure that regex special characters in the scenario names are ignored"
    feature = Feature.from_string(FEATURE19)

    assert feature.scenarios[0].tags == ('runme1',)

    assert feature.scenarios[1].tags == ('runme2',)


def test_background_parsing_with_mmf():
    """Test background parsing with description."""
    feature = Feature.from_string(FEATURE16)
    assert feature.description == \
        "As a rental store owner\n" \
        "I want to keep track of my clients\n" \
        "So that I can manage my business better"

    assert isinstance(feature.background, Background)
    assert feature.background.steps
    assert len(feature.background.steps) == 2

    step1, step2 = feature.background.steps
    assert step1.sentence == \
        'Given I have the following movies in my database:'
    assert_equal(step1.hashes, (
        {
            u'Available': u'6',
            u'Rating': u'4 stars',
            u'Name': u'Matrix Revolutions',
            u'New': u'no',
        },
        {
            u'Available': u'11',
            u'Rating': u'5 stars',
            u'Name': u'Iron Man 2',
            u'New': u'yes',
        },
    ))

    assert step2.sentence == \
        'And the following clients:'
    assert_equal(step2.hashes, (
        {u'Name': u'John Doe'},
        {u'Name': u'Foo Bar'},
    ))


def test_background_parsing_without_mmf():
    """Test background parsing without description."""
    feature = Feature.from_string(FEATURE17)
    assert feature.description == ""

    assert isinstance(feature.background, Background)
    assert feature.background.steps
    assert len(feature.background.steps) == 2

    step1, step2 = feature.background.steps
    assert step1.sentence == \
        'Given I have the following movies in my database:'
    assert_equal(step1.hashes, (
        {
            u'Available': u'6',
            u'Rating': u'4 stars',
            u'Name': u'Matrix Revolutions',
            u'New': u'no',
        },
        {
            u'Available': u'11',
            u'Rating': u'5 stars',
            u'Name': u'Iron Man 2',
            u'New': u'yes',
        },
    ))
    assert_equal(step1.table, (
        ('Name', 'Rating', 'New', 'Available'),
        ('Matrix Revolutions', '4 stars', 'no', '6'),
        ('Iron Man 2', '5 stars', 'yes', '11'),
    ))

    assert step2.sentence == \
        'And the following clients:'
    assert_equal(step2.hashes, (
        {u'Name': u'John Doe'},
        {u'Name': u'Foo Bar'},
    ))
    assert_equal(step2.table, (
        ('Name',),
        ('John Doe',),
        ('Foo Bar',),
    ))


def test_syntax_error_for_scenarios_with_no_name():
    ("Trying to parse features with unnamed "
     "scenarios will cause a syntax error")
    with assert_raises(AloeSyntaxError) as error:
        Feature.from_string(FEATURE20)

    assert_equal(
        error.exception.msg,
        "Syntax error at: None\n"
        "3:5 Scenario must have a name"
    )


def test_syntax_error_malformed_feature():
    """Parsing a malformed feature causes a syntax error."""

    with assert_raises(AloeSyntaxError) as error:
        Feature.from_string("""
PARSE ERROR
""")

    # pylint:disable=line-too-long
    assert_equal(error.exception.msg, '\n'.join((
        "Syntax error at: None",
        "Parser errors:",
        "(2:1): expected: #EOF, #Language, #TagLine, #FeatureLine, #Comment, #Empty, got 'PARSE ERROR'",
    )))
    # pylint:enable=line-too-long


def test_syntax_error_malformed_feature_from_file():
    """Parsing a malformed feature in a filecauses a syntax error."""

    with tempfile.NamedTemporaryFile() as feature_file:
        feature_file.write(b"""
PARSE ERROR
""")
        feature_file.flush()

        with assert_raises(AloeSyntaxError) as error:
            Feature.from_file(feature_file.name)

        # pylint:disable=line-too-long
        assert_equal(error.exception.msg, '\n'.join((
            "Syntax error at: {filename}",
            "Parser errors:",
            "(2:1): expected: #EOF, #Language, #TagLine, #FeatureLine, #Comment, #Empty, got 'PARSE ERROR'",
        )).format(filename=feature_file.name))
        # pylint:enable=line-too-long


def test_scenario_post_email():
    ("Having a scenario which the body has an email address; "
     "Then the following scenario should have no "
     "tags related to the email")

    feature = Feature.from_string(FEATURE21)
    scenario1, scenario2 = feature.scenarios

    assert scenario1.tags == ()
    assert scenario2.tags == ('tag',)


def test_feature_first_scenario_tag_extraction():
    ("A feature object should be able to find the single tag "
     "belonging to the first scenario")
    feature = Feature.from_string(FEATURE22)

    assert feature.scenarios[0].tags == ('onetag',)


def test_feature_first_scenario_tags_extraction():
    ("A feature object should be able to find the tags "
     "belonging to the first scenario")
    feature = Feature.from_string(FEATURE23)

    assert feature.scenarios[0].tags == \
        ('onetag', 'another', '$%^&even-weird_chars')
