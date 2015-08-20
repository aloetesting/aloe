# Line numbers in this file are tested against
Feature: Highlighting

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  # Comments are not shown

  Background:
    Given I have a table

  Scenario: behave_as works
    Given I have entered 10 into the calculator
    And I press [+]

  Scenario Outline: Scenario outlines
    Given I have entered <number> into the calculator
    And I press add

    Examples:
      | number |
      | 30     |
      | 40     |

  @tables
  Scenario: Scenario with table
    Given I have a table:
      | value |
      | 1     |
      | 1     |
      | 2     |

  Scenario: Scenario with a multiline
    Given I have a table:
    """
    Not actually a table :-P
    """
