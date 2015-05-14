Feature: Scenario indices

  As a programmer
  I want to run only some of the scenarios
  So that my feedback loop is short

  # The results are tested in the Python test

  Scenario: First scenario
    Given I have entered 10 into the calculator
    And I press add

  Scenario: Second scenario
    Given I have entered 20 into the calculator
    And I press add

  Scenario Outline: Scenario outline with two examples
    Given I have entered <number> into the calculator
    And I press add

    Examples:
      | number |
      | 30     |
      | 40     |
