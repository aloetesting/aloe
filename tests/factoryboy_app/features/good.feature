Feature: Test Factoryboy steps

    As an Aloe user
    I want to create objects using Factoryboy
    So that I can type less stuff


    Scenario: Create a user
        Given I have a user

        Then I made 1 user


    Scenario: Create a bunch of users
        Given I have 10 users

        Then I made 10 users


    Scenario: Create some users with specified info
        Given I have users:
            | username    |
            | danni       |
            | koterpillar |

        Then I made 2 users
        And passwd contains:
            | username    | email                   |
            | danni       | danni@example.org       |
            | koterpillar | koterpillar@example.org |


    Scenario: Bulk create users with specified info
        Given I have 3 users:
            | username |
            | jessie   |

        Then I made 3 users
        And passwd contains:
            | username | email              |
            | jessie   | jessie@example.org |
            | jessie   | jessie@example.org |
            | jessie   | jessie@example.org |
