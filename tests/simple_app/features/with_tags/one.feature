Feature: Scenario tags

  As a programmer
  I want to run only some predefined subsets of the scenarios
  So that my feedback loop is short

  # The results are tested in the Python test

  @hana
  Scenario: First scenario
    Given I have entered 1 into the calculator
    And I press add

  @dul
  Scenario: Second scenario
    Given I have entered 2 into the calculator
    And I press add

  @hana
  Scenario Outline: Another first scenario - surprise
    Given I have entered <number> into the calculator
    And I press add

    Examples:
      | number |
      | 11     |
      | 22     |

  Scenario: Fourth scenario
    Given I have entered 4 into the calculator
    And I press add
