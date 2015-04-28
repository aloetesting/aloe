Feature: Feature callbacks (test)

  Test the feature callback tests

  Scenario: Prepare more feature callbacks
    Given I emit a feature event of "C"

  Scenario: Test feature callbacks
    When I emit a feature event of "D"
    # Last two brackets are from the current feature
    Then the feature event sequence should be "{[AB]}{[CD"
