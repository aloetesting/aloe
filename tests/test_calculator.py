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

        # TODO: This should be a decorator on the function/class

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
            result = Runner(exit=False,
                            argv=['lychee', 'features/calculator.feature'])
            assert result.success

    def test_wrong_expectations(self):
        """
        Test that a failing feature fails tests.
        """

        with self.in_directory('tests/tested_app'):
            result = Runner(exit=False,
                            argv=['lychee',
                                  'features/wrong_expectations.feature'])
            assert not result.success
