Feature: Step callbacks

  Test step callbacks

  Scenario: Step callbacks
    Given I emit a step event of "A"
    And I emit a step event of "B"
    # Last two brackets are from the current example
    Then the step event sequence should be "{[A]}{[B]}{["
