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
Test code generation utilities.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import unittest
from contextlib import contextmanager

from aloe.codegen import (
    indent,
    make_function,
    multi_manager,
    remove_indent,
)


class TestCodegen(unittest.TestCase):
    """
    Test code generation.
    """

    def test_not_functions(self):
        """Test make_function error conditions."""
        with self.assertRaises(ValueError):
            make_function('1+1')

        with self.assertRaises(ValueError):
            make_function('def one(): pass\ndef two(): pass')

    def test_functions(self):
        """Test generating functions."""
        def inner(val):
            """A function to pass to the generated one."""
            return 2 * val

        adder = make_function(
            'def add(x, y): return inner(x) + y',
            context={
                'inner': inner,
            },
            name='adder',
        )
        self.assertEqual(adder(10, 3), 23)
        self.assertEqual(adder.__name__, 'adder')


class TestIndent(unittest.TestCase):
    """
    Test indentation utilities.
    """

    def test_indent(self):
        """Test indent()."""
        original = '\n'.join((
            'def one():',
            '    pass',
            '',
            'def two():',
            '    pass',
            '',
        ))

        self.assertEqual(indent(original), '\n'.join((
            '    def one():',
            '        pass',
            '',
            '    def two():',
            '        pass',
            '',
        )))

        self.assertEqual(indent(original, 3), '\n'.join((
            '            def one():',
            '                pass',
            '',
            '            def two():',
            '                pass',
            '',
        )))

    def test_remove_indent(self):
        """Test remove_indent()."""
        original = '\n'.join((
            '    def one():',
            '        pass',
            '',
            '    def two():',
            '        pass',
            '    ',
        ))

        self.assertEqual(remove_indent(original), '\n'.join((
            'def one():',
            '    pass',
            '',
            'def two():',
            '    pass',
            '',
        )))


class TestMultiManager(unittest.TestCase):
    """
    Test multi_manager.
    """

    @staticmethod
    def good_cm(order, i):
        """Generate a context manager logging to a given list."""
        @contextmanager
        def manager():
            """Context manager logging to a given list."""
            order.append('before cm {0}'.format(i))
            try:
                yield 'from cm {0}'.format(i)
            finally:
                order.append('after cm {0}'.format(i))

        return manager

    @staticmethod
    @contextmanager
    def bad_cm():
        """A context manager always raising an exception."""
        raise Exception

    def test_multi_manager(self):
        """Test combining context managers."""

        order = []

        multi_cm = multi_manager(self.good_cm(order, 1),
                                 self.good_cm(order, 2))

        with multi_cm() as (ctx1, ctx2):
            self.assertEqual(ctx1, 'from cm 1')
            self.assertEqual(ctx2, 'from cm 2')

        self.assertEqual(order, [
            'before cm 1',
            'before cm 2',
            'after cm 2',
            'after cm 1',
        ])

    def test_empty(self):
        """Test the trivial case - combining zero context managers."""
        with multi_manager()() as result:
            self.assertEqual(result, ())

        with multi_manager()('foo', 'bar') as result:
            self.assertEqual(result, ())

    def test_exceptions(self):
        """Test exception propagation."""
        order = []

        multi_cm = multi_manager(self.good_cm(order, 1),
                                 self.bad_cm,
                                 self.good_cm(order, 3))

        with self.assertRaises(Exception):
            with multi_cm() as (_, _):
                raise AssertionError("Should not succeed")

        self.assertEqual(order, [
            'before cm 1',
            'after cm 1',
        ])

    def test_args(self):
        """
        Test passing arguments to the invoked managers.
        """

        @contextmanager
        def yield_args(*args):
            """A context manager passing its arguments to the context."""
            yield args

        with multi_manager(yield_args, yield_args)('foo', 'bar') \
                as (args1, args2):
            self.assertEqual(args1, ('foo', 'bar'))
            self.assertEqual(args2, ('foo', 'bar'))
