# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from nose.tools import assert_equals

from lychee import strings


def test_represent_table():
    """
    Test representing a table
    """

    table = [
        ['name', 'age'],
        [u'Gabriel Falcão', 22],
        ['Miguel', 19],
    ]

    assert_equals(
        strings.represent_table(table),
        u"| name           | age |\n"
        u"| Gabriel Falcão | 22  |\n"
        u"| Miguel         | 19  |"
    )


def test_represent_table_escapes_pipe():
    """
    Test representing a table with escaping
    """

    table = [
        ['name', 'age'],
        [u'Gabriel | Falcão', 22],
        ['Miguel | Arcanjo', 19],
    ]

    assert_equals(
        strings.represent_table(table),
        '\n'.join((
            r"| name              | age |",
            r"| Gabriel \| Falcão | 22  |",
            r"| Miguel \| Arcanjo | 19  |",
        ))
    )


def test_represent_table_allows_empty():
    """
    Test representing a table with an empty cell
    """

    table = [
        ['name', 'age'],
        [u'Gabriel | Falcão', 22],
        ['Miguel | Arcanjo', ''],
    ]

    assert_equals(
        strings.represent_table(table),
        '\n'.join((
            r"| name              | age |",
            r"| Gabriel \| Falcão | 22  |",
            r"| Miguel \| Arcanjo |     |",
        ))
    )


def test_column_width():
    """strings.column_width"""

    assert_equals(
        strings.get_terminal_width(u"あいうえお"),
        10
    )


def test_column_width_w_number_and_char():
    """strings.column_width_w_number_and_char"""

    assert_equals(
        strings.get_terminal_width(u"%s%c" % (u"4209", 0x4209)),
        6
    )
