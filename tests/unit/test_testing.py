# -*- coding: utf-8 -*-
"""
Test step loading.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import unittest

from aloe.testing import (
    FeatureTest,
    in_directory,
)


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

    def test_run_good_feature_string_non_ascii(self):
        """
        Test running strings with non-ASCII symbols as features.
        """

        result = self.run_feature_string(
            """
            # language: zh-CN
            功能: Empty feature

            场景: Empty scenario
                当I do nothing
                那么I do nothing
            """
        )

        self.assertTrue(result.success)


def relative(directory):
    """
    A directory relative to the one containing this file.
    """

    return os.path.join(os.path.dirname(__file__), directory)


@in_directory(relative('../../tests/functional'))
class InDirectoryTest(unittest.TestCase):
    """
    Test in_directory.
    """

    def test_in_directory_on_class(self):
        """
        Test in_directory on the containing class.
        """

        self.assertTrue(os.getcwd().endswith('tests/functional'))

    @in_directory(relative('../../tests'))
    def test_in_directory_on_method(self):
        """
        Test in_directory on the method.
        """

        self.assertTrue(os.getcwd().endswith('tests'))
