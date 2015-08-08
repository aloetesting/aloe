# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Danielle Madeley <danielle@madeley.id.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Test step_from_factory
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

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

    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'john%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


@step(r'I made (\d+) users?')
def count_users(self, nusers):
    """Test the number of users I have made"""

    nusers = guess_types(nusers)
    assert_equal(nusers, len(User.users))


@step('passwd contains')
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
def clear_passwd(scenario, outline, steps):
    User.users = []
