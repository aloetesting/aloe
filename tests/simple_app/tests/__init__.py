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
Python tests for a test application.
"""

import os
import unittest


class NormalTestCase(unittest.TestCase):
    """
    Normal test which should not be picked up by the Gherkin runner.
    """

    @classmethod
    def setUpClass(cls):
        """
        Prevent the test from running in the main (Aloe) test suite.
        """

        if 'simple_app' not in os.getcwd():
            raise unittest.SkipTest()

    def test_failing_test(self):
        """
        A test to check whether the Python tests are running.
        """

        raise AssertionError("This test should not be run.")
