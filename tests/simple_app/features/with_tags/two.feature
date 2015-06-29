@dul
Feature: Scenario and feature tags

  As a programmer
  I want to run only some predefined subsets of the scenarios and features
  So that my feedback loop is short

  # The results are tested in the Python test

  @hana @set
  Scenario: First scenario
    Given I have entered 13 into the calculator
    And I press add

  Scenario: Second scenario
    Given I have entered 20 into the calculator
    And I press add

  Scenario: Another first scenario - surprise
    Given I have entered 200 into the calculator
    And I press add
