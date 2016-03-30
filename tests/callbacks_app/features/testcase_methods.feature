Feature: TestCase methods

  Test how scenarios correspond to TestCase tests

  Background:
    Given I emit a testclass event of "B"

  Scenario: Simple scenario
    When I emit a testclass event of "S"
    # Result tested back in the functional test

  Scenario Outline: Scenario Outline
    When I emit a testclass event of "<event>"
    # Result tested back in the functional test

    Examples:
      | event |
      | O     |
      | U     |
