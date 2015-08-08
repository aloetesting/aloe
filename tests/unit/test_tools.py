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
Test tool functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

import unittest
from datetime import date

from aloe.tools import guess_types


class GuessTypesTest(unittest.TestCase):
    """
    Test guess_types().
    """

    def test_simple_types(self):
        values = [
            ('a', 'a'),
            ('1', 1),
            ('01234', '01234'),  # not converted to oct
            ('false', False),
            ('true', True),
            ('null', None),
            ('2015-04-16', date(2015, 4, 16)),
        ]

        inputs_, outputs = zip(*values)

        self.assertEqual(list(map(guess_types, inputs_)),
                         list(outputs))

    def test_hashes(self):
        input_ = [{
            'name': 'Danni',
            'height': '178',
        }, {
            'name': 'Alexey',
            'height': '182',
        }]

        output_ = [{
            'name': 'Danni',
            'height': 178,
        }, {
            'name': 'Alexey',
            'height': 182,
        }]

        self.assertEqual(guess_types(input_),
                         output_)

    def test_table(self):
        input_ = [
            ['name', 'russian', 'german'],
            ['Danni', 'false', 'true'],
            ['Alexey', 'true', 'false'],
        ]

        output_ = [
            ['name', 'russian', 'german'],
            ['Danni', False, True],
            ['Alexey', True, False],
        ]

        self.assertEqual(guess_types(input_),
                         output_)
