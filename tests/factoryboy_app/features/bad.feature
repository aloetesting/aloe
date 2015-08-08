Feature: Test Factoryboy steps fail when expected

    As an Aloe user
    I want to create objects using Factoryboy
    So that I can type less stuff


    Scenario: Can't specify count and multiple rows (assert fails)
        Given I have 3 users:
            | username    |
            | jessie      |
            | danni       |
            | koterpillar |
