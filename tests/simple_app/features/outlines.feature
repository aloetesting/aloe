Feature: Add up different sets numbers

  As a thorough tester
  I want to check how different numbers add up
  So that I am sure of commutativity

  Scenario Outline: Add two numbers
    Given I have entered <num1> into the calculator
    And I have entered <num2> into the calculator
    And I have entered <num3> into the calculator
    When I press add
    Then the result should be 100 on the screen

    Examples:
      | num1 | num2 | num3 |
      | 20   | 30   | 50   |
      | 50   | 30   | 20   |
