Feature: Scenario indices

  As a programmer
  I want to see my scenarios with pretty highlighting
  So my output is easy to read

  # Comments are not shown

  Scenario: First scenario
    Given I have entered 10 into the calculator
    And I press add

  Scenario Outline: Scenario outline with two examples
    Given I have entered <number> into the calculator
    And I press add

    Examples:
      | number |
      | 30     |
      | 40     |

  Scenario: Scenario with table
    Given I press add:
      | value |
      | 1     |
      | 1     |
      | 2     |
