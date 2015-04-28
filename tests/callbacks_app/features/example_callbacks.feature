Feature: Example callbacks

  Test example callbacks

  Scenario: Example callbacks in a simple scenario
    Given I emit an example event of "A"
    And I emit an example event of "B"
    Then the example event sequence should be "{[AB"

  Scenario Outline: Example callbacks in a scenario with examples
    Given I emit an example event of "<event>"
    And I emit an example event of "E"
    # Tested in the next scenario

    Examples:
      | event |
      | C     |
      | D     |

  Scenario: Check the events from previous example
    # Last two brackets are from the current example
    Then the example event sequence should be "{[AB]}{[CE]}{[DE]}{["
