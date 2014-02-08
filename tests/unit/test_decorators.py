# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2014>  Danielle Madeley <danielle@madeley.id.au>
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

from nose.tools import assert_equals

from lettuce.decorators import memoizedproperty


def test_memoizedproperty():
    """
    Test @memoizedproperty
    """

    class Example(object):
        def __init__(self):
            self.prop_hits = 0

        @memoizedproperty
        def prop(self):
            """
            An expensive property
            """

            self.prop_hits += 1

            return 'A'

    example = Example()

    assert_equals(example.prop, 'A')
    assert_equals(example.prop, 'A')
    assert_equals(example.prop, 'A')
    assert_equals(example.prop, 'A')

    assert_equals(example.prop_hits, 1)
