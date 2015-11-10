Feature: behave_as

  Test calling behave_as on a step

  Background:
    Given I emit a step event of "Z"
    And I emit a step event for each letter in "BC"

  Scenario: Step callbacks
    Given I emit a step event of "A"
    And I emit a step event for each letter in "DE"
    # Last two brackets are from the current step
    Then the step event sequence should be "{[Z]}{[{[B]}{[C]}]}{[A]}{[{[D]}{[E]}]}{["

  Scenario Outline: behave_as works in scenario outlines
    Given I emit a step event for each letter in "<letters>"

    Examples:
      | letters |
      | AB      |
      | CD      |
