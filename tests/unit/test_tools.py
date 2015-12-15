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

import unittest
from datetime import date

from aloe.tools import guess_types


class GuessTypesTest(unittest.TestCase):
    """Test guess_types()"""

    def test_simple_types(self):
        """Test simple types"""
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
        """Test step.hashes structure"""
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
        """Test step.table structure"""
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
