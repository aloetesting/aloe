Feature: "All" callbacks (more preparation)

  Prepare more for the "all" callbacks

  Scenario: Prepare more "all" callbacks
    Given I emit an "all" event of "C"

  Scenario: Test "all" callbacks
    Given I emit an "all" event of "D"
    Then the "all" event sequence should be "{[ABCD"
