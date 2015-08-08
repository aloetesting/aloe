# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>
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
Test utility functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
import unittest

from contextlib import contextmanager
from functools import wraps

from aloe.utils import (
    unwrap_function,
    memoizedproperty,
)


def my_function():
    """A function to test unwrapping on."""
    pass  # pragma: no cover


class UnwrapTest(unittest.TestCase):
    """
    Test unwrapping functions.
    """

    def test_plain_function(self):
        """Test unwrapping the raw function."""

        self.assertEqual(unwrap_function(my_function), my_function)

    def test_wraps(self):
        """Test unwrapping a function from a decorator using wraps."""

        if sys.version_info < (3, 0):
            # In Python 2, functools doesn't set enough information on the
            # wrapped function
            raise unittest.SkipTest(
                "Cannot unwrap @wraps in general case on Python 2.")

        @wraps(my_function)
        def decorated():
            """A decorated function."""
            return my_function()

        self.assertEqual(unwrap_function(decorated), my_function)

    def test_contextmanager(self):
        """Test unwrapping a context manager."""

        self.assertEqual(
            unwrap_function(contextmanager(my_function)),
            my_function
        )


class MemoizedTest(unittest.TestCase):
    """Test memoization functions."""

    def test_memoizedproperty(self):
        """Test memoizedproperty."""

        class Memoized(object):
            """A class to test memoizedproperty."""

            def __init__(self, value):
                self.value = value

            @memoizedproperty
            def prop(self):
                """
                A property that intentionally modifies the instance state on
                every access.
                """

                self.value += 1
                return self.value

        first = Memoized(5)
        second = Memoized(10)

        # Test that multiple accesses don't result in multiple calls
        self.assertEqual(first.prop, 6)
        self.assertEqual(first.prop, 6)

        # Test that different objects aren't sharing the value
        self.assertEqual(second.prop, 11)
        self.assertEqual(second.prop, 11)
