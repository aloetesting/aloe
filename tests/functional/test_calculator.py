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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from . import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/tested_app')
class CalculatorTest(FeatureTest):
    """
    Test that calculator feature works as expected.
    """

    def test_calculator(self):
        """
        Test running the calculator feature.
        """

        self.assert_feature_success('features/calculator.feature')

    def test_wrong_expectations(self):
        """
        Test that a failing feature fails tests.
        """

        self.assert_feature_fail('features/wrong_expectations.feature')

    def test_background(self):
        """
        Test running a scenario with a background.
        """

        self.assert_feature_success('features/background.feature')

    def test_outlines(self):
        """
        Test a scenario with outlines.
        """

        self.assert_feature_success('features/outlines.feature')

    def test_python_test_skipped(self):
        """
        Test that the Python test does not get picked up.
        """

        self.assert_feature_success('tests')
