"""
Aloe integration with `factory_boy`_ to create objects from factories.

Remember when writing BDD tests to describe the behaviour you want and not just
use Aloe as a syntax for writing complex tests (that defeats the point of BDD).
Hide the complexity of setting up the objects in your factory or write a
custom step.

To activate these steps import :mod:`aloe.steps.factoryboy` into your
``steps/__init__.py``.

.. _factory_boy: https://factoryboy.readthedocs.org/en/latest/
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import

import re

from aloe import before, step
from aloe.utils import camel_case_to_spaces


def _run_factory(factory, self, count=None):
    """
    Run a factory using the step definition.
    """

    count = 1 if count is None else int(count)

    if self.table:
        headers = self.table[0]
        rows = tuple(
            dict(zip(headers, row))
            for row in self.table[1:]
        )
    else:
        rows = ({},)

    if count != 1 and len(rows) != 1:
        raise ValueError("Cannot specify count and a table together.")

    for row in rows:
        for _ in range(count):
            factory(**row)


def step_from_factory(factory):
    """
    Decorator to register a :class:`factory.Factory` as an Aloe step:

        Given/And I have (a/an/`n`) `object(s)`

    An optional table can be passed containing attributes that would be
    passed as `kwargs` to :meth:`factory.Factory.create`.
    Multiple rows or a number of objects can be passed to create more than one
    object. If a number of objects is requested, at most one row can be given,
    passed as `kwargs` to :meth:`factory.Factory.create_batch`.

    The name of the object and its plural are taken from
    :attr:`factory.Factory._meta` if set, or otherwise inferred from the
    class name.

    Example:

    .. code-block:: python

        @step_from_factory
        class RandomUserFactory(factory.Factory):
            '''See Factory Boy docs'''

            class Meta:
                model = models.User

            first_name = factory.Faker('first_name')
            last_name = factory.Faker('last_name')

    .. code-block:: gherkin

        Given I have a random user
        # Then I have created 1 user: Lucy Murray (a random name)

        Given I have 10 random users
        # Then I have created 10 users with different random names

        Given I have random users:
            | first_name | last_name |
            | Danielle   | Madeley   |
            | Alexey     | Kotlyarov |
        # Then I have created 2 users: Danni and Alexey

        Given I have 10 random users:
            | first_name |
            | Joe        |
        # Then I have created 10 users all with the first name Joe
    """

    try:
        name = factory._meta.verbose_name  # pylint:disable=protected-access
    except AttributeError:
        name = camel_case_to_spaces(
            re.sub('Factory$', '', factory.__name__))

    try:
        # pylint:disable=protected-access
        plural = factory._meta.verbose_name_plural
        # pylint:enable=protected-access
    except AttributeError:
        plural = name + 's'

    # pylint:disable=unused-variable
    # Functions are declared solely for the decorator side effects
    # (registering them as Lettuce steps and callbacks)

    @step(r'I have an? {name}:?$'.format(name=name))
    @step(r'I have(?: (\d+))? {plural}:?$'.format(plural=plural))
    def run_this_factory(self, count=1):
        """
        Run the factory using the step definition.
        """

        _run_factory(factory, self, count)

    @before.each_example
    def reset_this_factory(self, *args, **kwargs):
        """
        Reset this factory before each example.
        """

        try:
            factory.reset_sequence()
        except (ValueError, AttributeError):
            pass

    return factory
