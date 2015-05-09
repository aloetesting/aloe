Feature: Example callbacks

  Test example callbacks

  Background:
    Given I emit an example event of "Z"

  Scenario: Example callbacks in a simple scenario
    When I emit an example event of "A"
    And I emit an example event of "B"
    Then the example event sequence should be "{[ZAB"

  Scenario Outline: Example callbacks in a scenario with examples
    Given I emit an example event of "<event>"
    And I emit an example event of "E"
    # Tested in the next scenario

    Examples:
      | event |
      | C     |
      | D     |

  Scenario: Check the events from previous example
    # The unbalanced bit at the end is from the current example
    Then the example event sequence should be "{[ZAB]}{[ZCE]}{[ZDE]}{[Z"
