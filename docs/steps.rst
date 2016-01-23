Defining Steps
==============

.. toctree::
    :maxdepth: 2

.. autofunction:: aloe.step(sentence=None)

Common regular expressions for capturing data
---------------------------------------------

**String**

    .. code-block:: gherkin

        Given I logged in as "alexey"

    .. code-block:: python

        @step(r'I logged in as "([^"]*)"')

**Number**

    .. code-block:: gherkin

        Then the price should be $12.99

    .. code-block:: python

        @step(r'The price should be \$(\d+(?:\.\d+)?)')

**Path/URI/etc.**

    .. code-block:: gherkin

        Given I visit /user/alexey/profile

    .. code-block:: python

        @step(r'I visit ([^\s]+)')

Step Loading
------------

Steps can and should be defined in separate modules to the main application
code. Aloe searches for modules to load steps from inside the ``features``
directories.

Additional 3rd-party steps (such as `aloe_django`_) can be imported in from
your ``__init__.py``.

.. include:: links.rst

Tools for step writing
----------------------

.. toctree::
    :maxdepth: 2


.. automodule:: aloe.tools
    :members:

Writing good BDD steps
----------------------

It's very easy with BDD testing to accidentally reinvent Python testing
using a pseudo-language. Doing so removes much of the point of using BDD
testing in the first place, so here is some advice to help write better BDD
steps.

1.  **Avoid implementation details**

    If you find yourself specifying implementation details of your application
    that aren't important to your behaviors, abstract them into another
    step.

    Implementation:

    .. code-block:: gherkin

        When I fill in username with "danni"
        And I fill in password with "secret"
        And I press "Log on"
        And I wait for AJAX to finish

    Behavioral:

    .. code-block:: gherkin

        When I log on as "danni" with password "secret"

    You can use :meth:`Step.behave_as` to write a step that chains up several
    smaller steps.

    Implementation:

    .. code-block:: gherkin

        Given the following flags are set:
            | flags                      |
            | user_registration_disabled |
            | user_export_disabled       |

    Behavioral:

    .. code-block:: gherkin

        Given user registration is disabled
        And user export is disabled

    Remember you can generate related steps using a loop.

    .. code-block:: python

        for description, flag in ( ... ):
            @step(description + ' is enabled')
            def _enable_flag(self):

                set_flag(flag, enabled=True)

            @step(description + ' is disabled')
            def _disable_flag(self):

                set_flag(flag, enabled=False)

    Furthermore, steps that are needed by all features can be moved to a
    :func:`~aloe.before.each_example` callback.

    If you want to write reusable steps, you can sometimes mix behavior
    and declaration.

    .. code-block:: gherkin

        Then I should see results:
            | Business Name (primaryText) | Blurb (secondaryText) |
            | Pet Supplies.com            | An online store for…  |

2.  **Avoid conjunctions in steps**

    If you're writing a step that contains an `and` or other conjunction
    consider breaking your step into two.

    Bad:

    .. code-block:: gherkin

        When I log out and log back in as danni

    Good:

    .. code-block:: gherkin

        When I log out
        And I log in as danni

    You can pass state between steps using :attr:`world`.

3.  **Support natural language**

    It's easier to write tests if the language they support is natural,
    including things such as plurals.

    Unnatural:

    .. code-block:: gherkin

        Given there are 1 users in the database

    Natural:

    .. code-block:: gherkin

        Given there is 1 user in the database

    This can be done with regular expressions.

    .. code-block:: python

        @step('There (?:is|are) (\d+) users? in the database')
