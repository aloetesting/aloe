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

import os

from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/step_definition_app')
class StepLoadingTest(FeatureTest):
    """
    Test that calculator feature works as expected.
    """

    def test_single_feature(self):
        """
        Test running a single feature.
        """

        self.assert_feature_success('features/single.feature')

    def test_subdirectory_feature(self):
        """
        Test running a feature in a subdirectory.
        """

        self.assert_feature_success(
            'features/subdirectory/another.feature')

    def test_all_features(self):
        """
        Test running all the features without explicitly specifying them.

        Features not in packages (not_a_submodule, python_inside/package)
        should not be run.
        """

        result = self.assert_feature_success()
        self.assertEqual(result.tests_run, [
            os.path.abspath(feature) for feature in (
                'features/single.feature',
                'features/subdirectory/another.feature',
                'submodule/features/third.feature',
            )
        ])
