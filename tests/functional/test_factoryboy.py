"""
Test Factory Boy steps.
"""

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
