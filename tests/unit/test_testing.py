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
Test step loading.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from aloe import step
from aloe.testing import (
    FeatureTest,
    in_directory,
)


@step(r'I do nothing')
def trivial_step(self):  # pylint:disable=unused-argument
    """Trivial passing step."""
    pass


@step(r'I fail')
def failing_step(self):  # pylint:disable=unused-argument
    """Trivial failing step."""
    raise AssertionError("This step is meant to fail.")


@in_directory('tests/unit')
class FeatureTestTest(FeatureTest):
    """
    Test running features.
    """

    def test_run_good_feature_string(self):
        """
        Test running strings as features.
        """

        result = self.run_feature_string(
            """
            Feature: Empty feature

            Scenario: Empty scenario
                Given I do nothing
                Then I do nothing
            """
        )

        self.assertTrue(result.success)

    def test_run_feature_string_fail(self):
        """
        Test running a failing feature string.
        """

        result = self.run_feature_string(
            """
            Feature: Empty feature

            Scenario: Empty scenario
                Given I do nothing
                Then I fail
            """
        )

        self.assertFalse(result.success)

    def test_run_feature_string_parse_error(self):
        """
        Test running a misformatted feature string.
        """

        result = self.run_feature_string(
            """
            Not a feature
            """
        )

        self.assertFalse(result.success)
