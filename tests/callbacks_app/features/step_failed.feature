Feature: step.failed

  Test the values of step.failed in different moments

  Scenario: Test step.failed
    When I have a succeeding step
    And I have a succeeding step
    And I have a failing step
    # Tested in the caller
