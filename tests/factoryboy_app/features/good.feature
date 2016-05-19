Feature: Test Factory Boy steps

    As an Aloe user
    I want to create objects using Factory Boy
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
        And the user list contains:
            | username    | email                   |
            | danni       | danni@example.org       |
            | koterpillar | koterpillar@example.org |


    Scenario: Bulk create users with specified info
        Given I have 3 users:
            | username |
            | jessie   |

        Then I made 3 users
        And the user list contains:
            | username | email              |
            | jessie   | jessie@example.org |
            | jessie   | jessie@example.org |
            | jessie   | jessie@example.org |


    Scenario: Types are interpretted
        Given I have a weird object:
            | string | int | none | bool | date       |
            | string | 1   | null | true | 2015-02-28 |

        Then my weird object has the right types


    Scenario: Steps for plural names are registered correctly
        Given I have an agency:
            | name             |
            | Aperture Science |
        And I have agencies:
            | name       |
            | Black Mesa |
            | Combine    |
        And I have a boring agency
        And I have 2 mysterious agencies

        Then I made 6 agencies
