# -*- coding: utf-8 -*-
"""
Basic scenario tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
import os
from inspect import getsourcefile

from aloe import world

from aloe.testing import (
    FeatureTest,
    in_directory,
)
from aloe.utils import PY3, TestWrapperIO


@in_directory('tests/simple_app')
class SimpleScenarioTest(FeatureTest):
    """
    Test that basic feature running works as expected.
    """

    def test_success(self):
        """
        Test running a simple feature.
        """

        self.assert_feature_success('features/calculator.feature')

    def test_success_zh(self):
        """
        Test running a simple feature in Chinese.
        """

        self.assert_feature_success('features/calculator_zh.feature')

    def test_failure(self):
        """
        Test that a failing feature fails tests.
        """

        self.assert_feature_fail('features/wrong_expectations.feature')

    def test_error_message(self):
        """
        Check that the appropriate error messages are printed on failure.
        """

        stream = TestWrapperIO()

        failing_feature = 'features/wrong_expectations.feature'

        self.assert_feature_fail(failing_feature, '-n', '1', stream=stream)

        output = stream.getvalue()

        error_header = "FAIL: Fail at adding " + \
            "(features.wrong_expectations: Wrong expectations)"

        self.assertIn(error_header, output)

        feature_stack_frame = """
  File "{feature}", line 11, in Fail at adding
    Then the result should be 40 on the screen
        """.strip().format(feature=os.path.abspath(failing_feature))

        self.assertIn(feature_stack_frame, output)

        step_file = getsourcefile(sys.modules['features.steps'])

        step_stack_frame = """
  File "{step_file}", line 64, in assert_result
    assert world.result == float(result)
AssertionError
        """.strip().format(step_file=step_file)

        self.assertIn(step_stack_frame, output)

    def test_failure_zh(self):
        """
        Test that a failing feature in Chinese fails tests.
        """

        stream = TestWrapperIO()

        failing_feature = 'features/wrong_expectations_zh.feature'

        self.assert_feature_fail(failing_feature, stream=stream)

        # Check that the appropriate error messages were printed

        output = stream.getvalue()

        error_header = "FAIL: 添加两个数值 " + \
            "(features.wrong_expectations_zh: 不对的预期)"

        self.assertIn(error_header, output)

        if PY3:
            feature_stack_frame = """
  File "{feature}", line 12, in 添加两个数值
    那么结果应该是40
            """.strip().format(feature=os.path.abspath(failing_feature))

            self.assertIn(feature_stack_frame, output)
        else:
            # Cannot use non-ASCII method names in Python 2
            feature_stack_frame = """
  File "{feature}", line 12, in
            """.strip().format(feature=os.path.abspath(failing_feature))

            self.assertIn(feature_stack_frame, output)

            feature_code_line = "那么结果应该是40"
            self.assertIn(feature_code_line, output)

        step_file = getsourcefile(sys.modules['features.steps'])

        step_stack_frame = """
  File "{step_file}", line 64, in assert_result
    assert world.result == float(result)
AssertionError
        """.strip().format(step_file=step_file)

        self.assertIn(step_stack_frame, output)

    def test_step_not_found(self):
        """
        Check the behavior when a step is not defined.
        """

        stream = TestWrapperIO()

        failing_feature = 'features/step_not_found.feature'

        self.assert_feature_fail(failing_feature, stream=stream)

        output = stream.getvalue()

        error_header = "ERROR: Failure: NoDefinitionFound " + \
            "(The step r\"When I engage the warp drive\" is not defined)"

        self.assertIn(error_header, output)

    def test_step_not_found_zh(self):
        """
        Check the behavior when a step is not defined with a Chinese feature.
        """

        stream = TestWrapperIO()

        failing_feature = 'features/step_not_found_zh.feature'

        self.assert_feature_fail(failing_feature, stream=stream)

        output = stream.getvalue()

        error_header = "ERROR: Failure: NoDefinitionFound " + \
            "(The step r\"当我开曲速引擎\" is not defined)"

        self.assertIn(error_header, output)

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

    def test_error_message_outline(self):
        """
        Check that the appropriate error messages are printed on failure in a
        scenario outline.
        """

        stream = TestWrapperIO()

        failing_feature = 'features/wrong_expectations.feature'

        self.assert_feature_fail(failing_feature, '-n', '2', stream=stream)

        output = stream.getvalue()

        error_header = "FAIL: Fail repeatedly " + \
            "(features.wrong_expectations: Wrong expectations)"

        self.assertIn(error_header, output)

        # TODO: Why isn't the line indented with 6 spaces like in the file?
        feature_stack_frame = """
  File "{feature}", line 22, in Fail repeatedly
    | 50     |
        """.strip().format(feature=os.path.abspath(failing_feature))

        self.assertIn(feature_stack_frame, output)

        example_stack_frame = """
  File "{feature}", line 18, in Fail repeatedly
    Then the result should be <result> on the screen
        """.strip().format(feature=os.path.abspath(failing_feature))

        self.assertIn(example_stack_frame, output)

        step_file = getsourcefile(sys.modules['features.steps'])

        step_stack_frame = """
  File "{step_file}", line 64, in assert_result
    assert world.result == float(result)
AssertionError
        """.strip().format(step_file=step_file)

        self.assertIn(step_stack_frame, output)

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
