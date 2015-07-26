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
Test filesystem-related functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import unittest

from aloe.fs import path_to_module_name


class PathToModuleNameTest(unittest.TestCase):
    """
    Test path_to_module_name.
    """

    def test_path_to_module_name(self):
        """Test path_to_module_name."""

        self.assertEqual(
            'one.two.three',
            path_to_module_name('one/two/three.py')
        )

        self.assertEqual(
            'one.two',
            path_to_module_name('one/two/__init__.py')
        )
