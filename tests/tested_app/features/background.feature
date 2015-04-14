Feature: Rigged calculator

  As Mallory
  I want to make the user go crazy
  So that they no longer trust the calculator

  Background:
    Given I have entered 10 into the calculator

  Scenario: Add two numbers
    Given I have entered 20 into the calculator
    And I have entered 40 into the calculator
    When I press add
    Then the result should be 70 on the screen
