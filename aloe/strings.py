# -*- coding: utf-8 -*-
"""
Utilities for working with strings.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import str
from builtins import zip
# pylint:enable=redefined-builtin

import unicodedata


def represent_table(table, indent=0, cell_wrap=str):
    """
    Render a table

    cell_wrap is a method to wrap the cell values in
    """

    if not table:
        return ''

    # calculate the width of each column
    table = [[str(cell).replace('|', r'\|')
              for cell in row]
             for row in table]

    lengths = [
        max(
            get_terminal_width(cell)
            for cell in column
        )
        for column in zip(*table)  # transpose
    ]

    return '\n'.join(
        ' ' * indent +
        '| %s |' % ' | '.join(cell_wrap(ljust(cell, length))
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


def ljust(string, width):
    """
    A version of ljust that considers the terminal width (see
    get_terminal_width)
    """

    width -= get_terminal_width(string)

    return string + ' ' * width
