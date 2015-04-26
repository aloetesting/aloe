Feature: Step callbacks

  Test step callbacks

  Scenario: Step callbacks
    Given I emit a step event of "A"
    And I emit a step event of "B"
    Then the step event sequence should be "{A}{B}{"
