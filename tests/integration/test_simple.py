"""
Test running Aloe in a separate process, as the real users would.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import subprocess
import sys
import unittest

from aloe.testing import in_directory


ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


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

    def test_success_zh(self):
        """
        Test running a simple feature with non-ASCII characters, with verbose
        output.
        """

        exitcode, out = self.run_feature('features/calculator_zh.feature',
                                         '--verbosity=3',
                                         terminal=True)
        print(out)
        self.assertEqual(exitcode, 0, "Feature run successfully.")

    def test_failure(self):
        """
        Test running a failing feature.
        """

        exitcode, _ = self.run_feature('features/wrong_expectations.feature')
        self.assertNotEqual(exitcode, 0, "Feature run failed.")

    def run_feature(self, *args, **kwargs):
        """
        Run a feature and return the (exitcode, output) tuple.
        :param args: Arguments to pass to the Aloe subprocess
        :param terminal: Whether to run in a terminal
        :returns: (exit code, output)
        """

        # Python 2 doesn't support named kwargs after star-args
        terminal = kwargs.pop('terminal', False)
        if kwargs:
            raise TypeError("Invalid arguments.")

        args = [sys.executable, '-c', 'import aloe; aloe.main()'] + list(args)

        # Ensure Aloe itself is on the path
        old_pythonpath = os.environ.get('PYTHONPATH', None)
        os.environ['PYTHONPATH'] = ROOT_PATH
        try:

            if terminal:
                try:
                    import pty
                except ImportError:
                    raise unittest.SkipTest("PTY support unavailable.")

                chunks = [b'']

                def read(file_desc):
                    """Store the subprocess output."""
                    data = os.read(file_desc, 1024)
                    chunks.append(data)
                    return data

                status = pty.spawn(args, read)  # pylint:disable=assignment-from-no-return

                # On Python 2, pty.spawn doesn't return the exit code
                if status is None:
                    (_, status) = os.wait()  # pylint:disable=no-member

                return status, b''.join(chunks)

            try:
                output = subprocess.check_output(
                    args,
                    stderr=subprocess.STDOUT,
                )
                return 0, output
            except subprocess.CalledProcessError as ex:
                return ex.returncode, ex.output

        finally:
            if old_pythonpath is None:
                del os.environ['PYTHONPATH']
            else:
                os.environ['PYTHONPATH'] = old_pythonpath
