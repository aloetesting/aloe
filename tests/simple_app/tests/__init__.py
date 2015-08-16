"""
Python tests for a test application.
"""

import os
import unittest


class NormalTestCase(unittest.TestCase):
    """
    Normal test which should not be picked up by the Gherkin runner.
    """

    @classmethod
    def setUpClass(cls):
        """
        Prevent the test from running in the main (Aloe) test suite.
        """

        if 'simple_app' not in os.getcwd():
            raise unittest.SkipTest()

    def test_failing_test(self):
        """
        A test to check whether the Python tests are running.
        """

        raise AssertionError("This test should not be run.")
