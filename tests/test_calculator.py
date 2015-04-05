import os
import unittest
from contextlib import contextmanager

from lychee.runner import Runner


class CalculatorTest(unittest.TestCase):
    """
    Test that calculator feature works as expected.
    """

    @staticmethod
    @contextmanager
    def in_directory(directory):
        """
        A context manager to change the current directory.
        """

        cwd = os.getcwd()
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(cwd)

    def test_calculator(self):
        """
        Test running the calculator feature.
        """

        with self.in_directory('tests/tested_app'):
            result = Runner(exit=False)
            assert result.success
