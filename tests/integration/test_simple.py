"""
Test running Aloe in a separate process, as the real users would.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import subprocess
import unittest

from aloe.testing import in_directory


ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MAIN = os.path.join(ROOT_PATH, 'aloe', '__init__.py')


@in_directory('tests/simple_app')
class SimpleIntegrationTest(unittest.TestCase):
    """
    Test that basic feature running works as expected.
    """

    def test_success(self):
        """
        Test running a simple feature.
        """

        exitcode, _ = self.run_feature('features/calculator.feature')
        self.assertEqual(exitcode, 0, "Feature run successfully.")

    def test_failure(self):
        """
        Test running a failing feature.
        """

        exitcode, _ = self.run_feature('features/wrong_expectations.feature')
        self.assertNotEqual(exitcode, 0, "Feature run failed.")

    def run_feature(self, *args):
        """
        Run a feature and return the (exitcode, output) tuple.
        """

        # Ensure Aloe itself is on the path
        env = os.environ.copy()
        env['PYTHONPATH'] = ROOT_PATH

        try:
            output = subprocess.check_output(
                (MAIN,) + args,
                stderr=subprocess.STDOUT,
                env=env,
            )
            return 0, output
        except subprocess.CalledProcessError as ex:
            return ex.returncode, ex.output
