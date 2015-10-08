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

        Neither features not in packages
        (not_a_submodule, python_inside/package)
        nor features not in directories named "features" should be run.
        """

        result = self.assert_feature_success()
        self.assertEqual(result.tests_run, [
            os.path.abspath(feature) for feature in (
                'features/single.feature',
                'features/subdirectory/another.feature',
                'submodule/features/third.feature',
            )
        ])


@in_directory('tests/not_a_package')
class NoRootPackageTest(FeatureTest):
    """
    Test running features from outside a package.
    """

    def test_no_package(self):
        """
        Test running features from outside a package.
        """

        # The only feature in this directory has steps but there are no
        # definitions for them anywhere, so it will fail if found.
        self.assert_feature_success()
