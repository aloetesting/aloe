# Lychee - Cucumber runner for Python based on Lettuce and Nose
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

from lychee.codegen import (
    indent,
    make_function,
    remove_indent,
)


class TestCodegen(unittest.TestCase):
    def test_not_functions(self):
        with self.assertRaises(ValueError):
            make_function('1+1')

        with self.assertRaises(ValueError):
            make_function('def one(): pass\ndef two(): pass')

    def test_functions(self):
        def inner(x):
            return 2 * x

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
    def test_indent(self):
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
