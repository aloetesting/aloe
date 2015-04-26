import os
import unittest


class NormalTestCase(unittest.TestCase):
    """
    Normal test which should not be picked up by the Gherkin runner.
    """

    @classmethod
    def setUpClass(cls):
        """
        Prevent the test from running in the main (Lychee) test suite.
        """

        if 'tested_app' not in os.getcwd():
            raise unittest.SkipTest()

    def test_failing_test(self):
        raise AssertionError("This test should not be run.")
