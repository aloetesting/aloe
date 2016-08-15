# -*- coding: utf-8 -*-
"""
Test utilities from aloe.strings.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import unittest

from aloe import strings


class StringsTest(unittest.TestCase):
    """Test utilities from aloe.strings."""

    def test_represent_table(self):
        """
        Test representing a table
        """

        table = [
            ['name', 'age'],
            [u'Gabriel Falcão', 22],
            ['Miguel', 19],
        ]

        self.assertEqual(
            strings.represent_table(table),
            u"| name           | age |\n"
            u"| Gabriel Falcão | 22  |\n"
            u"| Miguel         | 19  |"
        )

    def test_represent_table_escapes_pipe(self):
        """
        Test representing a table with escaping
        """

        table = [
            ['name', 'age'],
            [u'Gabriel | Falcão', 22],
            ['Miguel | Arcanjo', 19],
        ]

        self.assertEqual(
            strings.represent_table(table),
            '\n'.join((
                r"| name              | age |",
                r"| Gabriel \| Falcão | 22  |",
                r"| Miguel \| Arcanjo | 19  |",
            ))
        )

    def test_represent_table_allows_empty(self):
        """
        Test representing a table with an empty cell
        """

        table = [
            ['name', 'age'],
            [u'Gabriel | Falcão', 22],
            ['Miguel | Arcanjo', ''],
        ]

        self.assertEqual(
            strings.represent_table(table),
            '\n'.join((
                r"| name              | age |",
                r"| Gabriel \| Falcão | 22  |",
                r"| Miguel \| Arcanjo |     |",
            ))
        )

    def test_column_width(self):
        """strings.column_width"""

        self.assertEqual(
            strings.get_terminal_width(u"あいうえお"),
            10
        )

    def test_column_width_w_number_and_char(self):
        """strings.column_width_w_number_and_char"""

        self.assertEqual(
            strings.get_terminal_width(u"%s%c" % (u"4209", 0x4209)),
            6
        )
