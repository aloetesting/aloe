"""
Test utility functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future.utils import with_metaclass

import sys
import unittest

from contextlib import contextmanager
from functools import wraps

from aloe.utils import (
    unwrap_function,
    memoizedproperty,
    memoizedtype,
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

    def test_memoizedtype(self):
        """Test memoizedtype."""

        class Memoized(with_metaclass(memoizedtype, object)):
            """A class to test memoizedtype."""

            counter = 0

            def __init__(self, value):
                """
                A constructor that intentionally modifies the class state.
                """

                self.value = value
                # pylint:disable=no-member
                # https://bitbucket.org/logilab/pylint/issues/707
                type(self).counter += 1
                # pylint:enable=no-member

        first = Memoized(5)
        second = Memoized(10)

        # Check the objects are created properly
        self.assertEqual(first.value, 5)
        self.assertEqual(second.value, 10)

        # Try to create the same object again
        another_first = Memoized(5)

        # It should be the same as before
        self.assertIs(first, another_first)

        # Only two objects should have been created
        self.assertEqual(Memoized.counter, 2)
