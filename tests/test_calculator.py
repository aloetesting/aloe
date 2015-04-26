# Lychee - Cucumber runner for Python based on Lettuce and Nose
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
Basic scenario tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import os
import unittest
from contextlib import contextmanager

from lychee.runner import Runner


class CalculatorTest(unittest.TestCase):
    """
    Test that calculator feature works as expected.
    """

    def setUp(self):
        """
        Ensure inner Nose doesn't redirect output.
        """

        os.environ['NOSE_NOCAPTURE'] = '1'

    @staticmethod
    @contextmanager
    def in_directory(directory):
        """
        A context manager to change the current directory.
        """

        # TODO: This should be a decorator on the function/class

        cwd = os.getcwd()
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(cwd)

    def run_features(self, *features):
        """
        Run the specified features.
        """

        return Runner(exit=False,
                      argv=['lychee'] + list(features))

    def test_calculator(self):
        """
        Test running the calculator feature.
        """

        with self.in_directory('tests/tested_app'):
            result = self.run_features('features/calculator.feature')
            assert result.success

    def test_wrong_expectations(self):
        """
        Test that a failing feature fails tests.
        """

        with self.in_directory('tests/tested_app'):
            result = self.run_features('features/wrong_expectations.feature')
            assert not result.success

    def test_background(self):
        """
        Test running a scenario with a background.
        """

        with self.in_directory('tests/tested_app'):
            result = self.run_features('features/background.feature')
            assert result.success

    def test_outlines(self):
        """
        Test a scenario with outlines.
        """

        with self.in_directory('tests/tested_app'):
            result = self.run_features('features/outlines.feature')
            assert result.success

    def test_python_test_skipped(self):
        """
        Test that the Python test does not get picked up.
        """

        with self.in_directory('tests/tested_app'):
            result = self.run_features('tests')
            assert result.success
