# -*- coding: utf-8 -*-
# Lychee - Cucumber runner for Python based on Lettuce and Nose
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

"""
Main module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
import threading

from lychee.registry import (
    after,
    around,
    before,
    step,
)

world = threading.local()


def main(argv=None):  # pragma: no cover
    """
    Entry point for running Lychee.
    """

    if argv is None:
        argv = sys.argv

    from lychee.runner import Runner
    Runner(argv)

if __name__ == '__main__':  # pragma: no cover
    main()
