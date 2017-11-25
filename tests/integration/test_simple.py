"""
Test running Aloe in a separate process, as the real users would.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import re
from subprocess import check_output, STDOUT, CalledProcessError
import sys
import unittest

from aloe.testing import in_directory

from tests.utils import set_environ


TEST_PATH = os.path.dirname(__file__)

ROOT_PATH = os.path.dirname(os.path.dirname(TEST_PATH))

WINDOWS = os.name == 'nt'


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

        self.assertEqual(exitcode, 0, "Feature run successfully.")

        # Remove timing information from the output as unstable
        out = re.sub(b'in [0-9.]+s', b'in XXXXs', out)

        if WINDOWS:  # Windows uses different escape codes
            if sys.version_info[0] == 2:    # Python 2 decodes output
                expected_out_file = 'calculator_windows_py2.txt'
            else:
                expected_out_file = 'calculator_windows.txt'
        else:
            expected_out_file = 'calculator.txt'
        with open(os.path.join(TEST_PATH, expected_out_file), 'rb') as expected:
            expected_out = expected.read()
        self.assertEqual(out, expected_out, "Output matches expected.")

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
        with set_environ('PYTHONPATH', ROOT_PATH):

            if terminal and not WINDOWS:  # No pty on Windows
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

                with set_environ('TERM', 'xterm-256color'):

                    status = pty.spawn(args, read)  # pylint:disable=assignment-from-no-return

                    # On Python 2, pty.spawn doesn't return the exit code
                    if status is None:
                        (_, status) = os.wait()  # pylint:disable=no-member

                    return status, b''.join(chunks)

            try:
                output = check_output(args, stderr=STDOUT)
                return 0, output
            except CalledProcessError as ex:
                return ex.returncode, ex.output
