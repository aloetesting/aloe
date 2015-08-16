"""
Test Factory Boy steps.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
from future import standard_library
standard_library.install_aliases()

from aloe.testing import (
    FeatureTest,
    in_directory,
)


@in_directory('tests/factoryboy_app')
class FactoryBoyTest(FeatureTest):
    """
    Test Factory Boy steps.
    """

    def test_factoryboy(self):
        """
        Test Factory Boy steps.
        """

        self.assert_feature_success('features/good.feature')
        self.assert_feature_fail('features/bad.feature')
