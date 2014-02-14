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

import unicodedata


def utf8_string(s):
    if isinstance(s, str):
        s = s.decode("utf-8")

    return s


def represent_table(table, indent=0, cell_wrap=lambda s: s):
    """
    Render a table

    cell_wrap is a method to wrap the cell values in
    """

    if not table:
        return ''

    # calculate the width of each column
    table = [[unicode(cell).replace('|', r'\|')
              for cell in row]
             for row in table]
    lengths = [len(cell) for cell in table[0]]

    for row in table[1:]:
        lengths = map(max, zip(lengths, [len(cell) for cell in row]))

    return u'\n'.join(
        u' ' * indent +
        u'| %s |' % u' | '.join(cell_wrap(cell.ljust(length))
                                for cell, length in zip(row, lengths))
        for row in table
    )


def get_terminal_width(string):
    """
    Get the terminal width of a string

    This is not the length in characters, but the width that the characters
    will be displayed on a terminal, compensating for double-wide characters.
    """

    widths = {
        'W': 2,
        'F': 2,
    }

    return sum(widths.get(unicodedata.east_asian_width(c), 1) for c in string)


def ljust(string, n):
    """
    A version of ljust that considers the terminal width (see
    get_terminal_width)
    """

    n -= get_terminal_width(string)

    return string + u' ' * n
