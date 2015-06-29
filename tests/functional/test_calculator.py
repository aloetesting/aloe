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

from aloe import world

from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/simple_app')
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

    def test_scenario_indices(self):
        """
        Test specifying the scenario indices to run.
        """

        feature = 'features/scenario_index.feature'

        # Run a single scenario
        self.assert_feature_success(feature, '-n', '1')
        self.assertEqual(world.all_results, [10])

        # Run multiple scenarios
        # TODO: Handling multi-valued options in Nose is tricky
        self.assert_feature_success(feature, '-n', '1,2')
        self.assertEqual(world.all_results, [10, 20])

        # Run a scenario outline
        self.assert_feature_success(feature, '-n', '3')
        self.assertEqual(world.all_results, [30, 40])

    def test_tags(self):
        """
        Test specifying the tags to run.
        """

        feature_dir = 'features/with_tags'
        feature_one = 'features/with_tags/one.feature'
        feature_two = 'features/with_tags/two.feature'

        # Run scenarios by tag
        self.assert_feature_success(feature_one, '-a', 'hana')
        self.assertEqual(world.all_results, [10, 11])

        # Run scenarios with a tag that's not there
        self.assert_feature_success(feature_one, '-a', 'set')
        self.assertEqual(world.all_results, [])
