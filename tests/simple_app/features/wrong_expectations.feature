# Line numbers in this file are tested against
Feature: Wrong expectations

  This feature is intended to raise an assertion failure

  Scenario: Add two numbers
    Given I have entered 10 into the calculator
    And I have entered 20 into the calculator
    When I press add
    # The feature will fail here
    Then the result should be 40 on the screen
