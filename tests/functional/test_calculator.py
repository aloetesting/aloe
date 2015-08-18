"""
Basic scenario tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from os.path import dirname

from aloe import world

from aloe.testing import (
    FeatureTest,
    in_directory,
)
from aloe.utils import str_io


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

    def test_failure(self):
        """
        Test that a failing feature fails tests.
        """

        stream = str_io()

        self.assert_feature_fail('features/wrong_expectations.feature',
                                 stream=stream)

        # Check that the appropriate error messages were printed

        output = stream.getvalue()

        error_header = "FAIL: Add two numbers " + \
            "(features.wrong_expectations: Wrong expectations)"

        self.assertIn(error_header, output)

        feature_stack_frame = """
  File "{root}/tests/simple_app/features/wrong_expectations.feature", line 11, in Add two numbers
    Then the result should be 40 on the screen
        """.strip().format(root=dirname(dirname(dirname(__file__))))  # noqa

        self.assertIn(feature_stack_frame, output)

        step_stack_frame = """
  File "{root}/tests/simple_app/features/steps.py", line 60, in assert_result
    assert world.result == float(result)
AssertionError
        """.strip().format(root=dirname(dirname(dirname(__file__))))

        self.assertIn(step_stack_frame, output)

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

        # Run scenarios by tag
        self.assert_feature_success(feature_one, '-a', 'hana')
        self.assertEqual(world.all_results, [1, 11])

        # Run scenarios with a tag that's not there
        self.assert_feature_success(feature_one, '-a', 'set')
        self.assertEqual(world.all_results, [])

        # Run features and scenarios with the tag
        self.assert_feature_success(feature_dir, '-a', 'dul')
        self.assertEqual(world.all_results, [2, 13, 20, 200])

        # Specify a tag to exclude
        self.assert_feature_success(feature_one, '-a', '!hana')
        self.assertEqual(world.all_results, [2, 4])

        # Specify more than one tag to run
        self.assert_feature_success(feature_one, '-a', 'hana', '-a', 'dul')
        self.assertEqual(world.all_results, [1, 2, 11])

        # Specify more than one tag to exclude
        self.assert_feature_success(feature_dir, '-a', '!hana,!dul')
        self.assertEqual(world.all_results, [4])
