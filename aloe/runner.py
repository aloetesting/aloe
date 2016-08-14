"""
Unittest main working with Gherkin tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin

import os
import unittest

from importlib import import_module

from aloe.plugin import GherkinLoader
from aloe.result import AloeTestResult
from aloe.testclass import TestCase


class GherkinRunner(unittest.runner.TextTestRunner):
    """
    A test runner with Aloe result class.
    """

    resultclass = AloeTestResult


class TestProgram(unittest.TestProgram):
    """
    A test program loading Gherkin tests.
    """

    gherkin_loader = GherkinLoader
    test_class = TestCase
    runner = GherkinRunner

    def __init__(self, *args, **kwargs):
        """
        Enable Gherkin loading plugins and run the tests.
        """

        kwargs.setdefault('testLoader', self.gherkin_loader())
        kwargs.setdefault('testRunner', self.runner)
        super().__init__(*args, **kwargs)

    def _getMainArgParser(self, parent):
        """Add arguments specific to Aloe."""

        parser = super()._getMainArgParser(parent)

        test_class_name = \
            '{c.__module__}.{c.__name__}'.format(c=self.test_class)
        # Accept the old NOSE_GHERKIN_CLASS environment variable as well as
        # GHERKIN_CLASS
        for test_class_var in ('NOSE_GHERKIN_CLASS', 'GHERKIN_CLASS'):
            if test_class_var in os.environ:
                test_class_name = os.environ[test_class_var]

        parser.add_argument(
            '--test-class', action='store',
            dest='test_class_name',
            default=test_class_name,
            metavar='TEST_CLASS',
            help='Base class to use for the generated tests',
        )
        parser.add_argument(
            '--no-ignore-python', action='store_false',
            dest='ignore_python',
            default=True,
            help='Run Python and Gherkin tests together',
        )
        parser.add_argument(
            '-n', '--scenario-indices', action='store',
            dest='scenario_indices',
            default='',
            help='Only run scenarios with these indices (comma-separated)',
        )
        parser.add_argument(
            '--color', action='store_true',
            dest='force_color',
            default=False,
            help='Force colored output',
        )
        parser.add_argument(
            '--tag', action='append', dest='tags',
            help=(
                'Run only tests with the specified tag. '
                'Can be used multiple times.'
            ),
        )
        parser.add_argument(
            '--exclude-tag', action='append', dest='exclude_tags',
            help=(
                'Do not run tests with the specified tag. '
                'Can be used multiple times.'
            ),
        )

        return parser

    def createTests(self):
        """Set up loader before running tests."""

        self.setup_loader()

        return super().createTests()

    def _do_discovery(self, *args, **kwargs):
        """Set up loader before running discovery."""

        self.setup_loader()

        return super()._do_discovery(*args, **kwargs)

    def setup_loader(self):
        """Pass extra options to the test loader."""

        # These options are put onto self by parseArgs from the base class
        # pylint:disable=no-member
        self.testLoader.force_color = self.force_color
        self.testLoader.ignore_python = self.ignore_python

        if self.scenario_indices:
            self.testLoader.scenario_indices = tuple(
                int(index)
                for index in self.scenario_indices.split(',')
            )
        else:
            self.testLoader.scenario_indices = None

        module_name, class_name = self.test_class_name.rsplit('.', 1)
        module = import_module(module_name)
        self.testLoader.test_class = getattr(module, class_name)

        self.testLoader.tags = set(self.tags or ())
        self.testLoader.exclude_tags = set(self.exclude_tags or ())

    def runTests(self):
        """Run the "all" level callbacks."""

        self.testLoader.run_before_callbacks()
        super().runTests()
        self.testLoader.run_after_callbacks()
