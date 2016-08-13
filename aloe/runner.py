"""
Nose test runner with Gherkin plugin enabled.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin

import unittest

from aloe.plugin import GherkinLoader
from aloe.result import AloeTestResult


class AloeTestRunner(unittest.runner.TextTestRunner):
    """
    A test runner with Aloe result class.
    """

    resultclass = AloeTestResult


class Runner(unittest.TestProgram):
    """
    A test program loading Gherkin tests.
    """

    gherkin_loader = GherkinLoader

    def __init__(self, *args, **kwargs):
        """
        Enable Gherkin loading plugins and run the tests.
        """

        kwargs.setdefault('testLoader', self.gherkin_loader())
        kwargs.setdefault('testRunner', AloeTestRunner)
        super().__init__(*args, **kwargs)
