"""
Test feature loading across a symlink.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os

from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/symlink_follow_app/working_path')
class SymlinkLoadingTest(FeatureTest):
    """
    Test that symlink feature is discovered and evaluated.
    """

    def test_symlinked_feature(self):
        """
        Test that we can discover feature in a symlinked module.
        """

        result = self.assert_feature_success()
        self.assertEqual(
            result.tests_run,
            [os.path.abspath('common_app/features/symlinked.feature')]
        )
