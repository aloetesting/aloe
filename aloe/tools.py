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
Tools for writing Aloe steps.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

import re
from datetime import datetime


def guess_types(data):
    """
    Converts a record or list of records from outlines, table or hashes
    into a version with the types guessed.

    :param data: a :class:`Scenario.outlines`, :class:`Step.table` or
        :class:`Step.hashes` or entry

    Will guess the following in priority order:

     # bool (``true``/``false``)
     # None (``null``)
     # int
     # datetime in ISO format (2015-08-25)
     # str

    The function operates recursively, so you should be able to pass nearly
    anything to it. At the very least basic types plus dict and iterables.
    """

    # convert bytes to strings
    if isinstance(data, bytes):
        data = data.decode()

    if isinstance(data, str):
        if data == "true":
            return True
        elif data == "false":
            return False
        elif data == "null":
            return None
        elif data.isdigit() and not re.match("^0[0-9]+", data):
            return int(data)
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', data):
            return datetime.strptime(data, "%Y-%m-%d")

        # it's a string
        return data

    # if it's a dict, recurse as a dict
    if isinstance(data, dict):
        return {
            guess_types(key): guess_types(data)
            for key, data in data.items()
        }

    # try to recurse as an iterable
    try:
        return [guess_types(val) for val in data]
    except TypeError:
        pass

    #  give up
    return data
