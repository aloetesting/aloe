"""
Test step_from_factory
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import

from datetime import date

import factory

from aloe import step, after
from aloe.tools import guess_types
from aloe.steps.factoryboy import step_from_factory
from nose.tools import assert_equal


class User(object):
    """A user"""

    users = []

    def __init__(self, username, email):
        self.username = username
        self.email = email

        self.users.append(self)

    def __str__(self):
        return '%s (%s)' % (self.username, self.email)


@step_from_factory
class UserFactory(factory.Factory):
    """Factory to build a user"""

    class Meta(object):
        """Meta"""
        model = User

    username = factory.Sequence(lambda n: 'john%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


@step(r'I made (\d+) users?')
def count_users(self, nusers):
    """Test the number of users I have made"""

    nusers = guess_types(nusers)
    assert_equal(nusers, len(User.users))


@step('the user list contains')
def check_users(self):
    """Look for users in my user list"""

    expected = guess_types(self.hashes)
    actual = [{
        'username': obj.username,
        'email': obj.email,
    } for obj in User.users]

    print(actual)

    assert_equal(expected, actual)


@after.each_example
def clear_user_list(scenario, outline, steps):
    """Clear the user list between tests"""
    User.users = []


class Agency(object):
    """An agency. This object has non-trivial plural name."""

    agencies = []

    class _meta(object):
        """Meta, defined to mimic Django models."""

        verbose_name = "agency"
        verbose_name_plural = "agencies"

    def __init__(self, name):
        self.name = name

        self.agencies.append(self)


@step_from_factory
class AgencyFactory(factory.Factory):
    """Factory to build an agency."""

    class Meta(object):
        """Meta"""
        model = Agency

    name = factory.LazyAttribute(lambda n: 'agency%s' % n)


@step_from_factory
class BoringAgencyFactory(AgencyFactory):
    """Customized factory to build agencies."""

    # This factory will have registered steps according to its name - "boring
    # agency"
    pass


@step_from_factory
class SecretAgencyFactory(AgencyFactory):
    """Another customized factory to build agencies."""

    _verbose_name = "mysterious agency"
    _verbose_name_plural = "mysterious agencies"


@step(r'I made (\d+) (?:agency|agencies)')
def count_agencies(self, nagencies):
    """Test the number of agencies I have made"""

    nagencies = guess_types(nagencies)
    assert_equal(nagencies, len(Agency.agencies))


@step('the agency list contains')
def check_agencies(self):
    """Look for agencies in my agency list"""

    expected = guess_types(self.hashes)
    actual = [{
        'name': obj.name,
    } for obj in Agency.agencies]

    print(actual)

    assert_equal(expected, actual)


@after.each_example
def clear_agency_list(scenario, outline, steps):
    """Clear the agency list between tests"""
    Agency.agencies = []


class MyWeirdObject(object):
    """An object with different types"""

    ref = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        MyWeirdObject.ref = self


@step_from_factory
class WeirdObjectFactory(factory.Factory):
    """Factory to create MyWeirdObject"""

    class Meta(object):
        """Meta"""

        model = MyWeirdObject


@step('my weird object has the right types')
def check_types(self):
    """Check the types of MyWeirdObject"""

    for attr, type_ in (('string', type('')),  # get right type in Py2/3
                        ('int', int),
                        ('none', type(None)),
                        ('bool', bool),
                        ('date', date)):
        assert_equal(type(getattr(MyWeirdObject.ref, attr)), type_)
