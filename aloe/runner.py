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

import argparse
import os
import unittest

from importlib import import_module

from aloe.loader import GherkinLoader
from aloe.result import AloeTestResult
from aloe.testclass import TestCase
from aloe.utils import callable_type, PY2


class GherkinRunner(unittest.runner.TextTestRunner):
    """
    A test runner with Aloe result class.
    """

    def __init__(self, *args, **kwargs):
        """Remember the extra arguments."""
        self.force_color = kwargs.pop('force_color')
        super().__init__(*args, **kwargs)

    def resultclass(self, *args, **kwargs):  # pylint:disable=method-hidden
        """Construct an overridden result with extra arguments."""
        kwargs['force_color'] = self.force_color
        return AloeTestResult(*args, **kwargs)


class TestProgram(unittest.TestProgram):
    """
    A test program loading Gherkin tests.
    """

    gherkin_loader = GherkinLoader
    test_class = TestCase

    # Options set by parsing arguments
    force_color = False
    ignore_python = True
    scenario_indices = ''
    tags = []
    exclude_tags = []

    def __init__(self, *args, **kwargs):
        """
        Enable Gherkin loading plugins and run the tests.
        """

        if 'GHERKIN_TEST_CLASS' in os.environ:
            self.test_class_name = os.environ['GHERKIN_TEST_CLASS']
        else:
            self.test_class_name = \
                '{c.__module__}.{c.__name__}'.format(c=self.test_class)

        kwargs.setdefault('testLoader', self.gherkin_loader())
        kwargs.setdefault('testRunner', callable_type(self.make_runner))
        super().__init__(*args, **kwargs)

    def make_runner(self, *args, **kwargs):
        """Pass extra arguments to the test runner."""
        kwargs.update(self.extra_runner_args())
        return GherkinRunner(*args, **kwargs)

    def extra_runner_args(self):
        """Extra arguments to pass to the test runner."""

        return {
            'force_color': self.force_color,
        }

    def parseArgs(self, argv):
        """
        On Python 2, extract the Aloe arguments from the command line before
        passing on.
        """

        if PY2:
            parser = argparse.ArgumentParser(add_help=False)
            self.add_aloe_options(parser)
            _, argv = parser.parse_known_args(argv, self)

        return super().parseArgs(argv)

    def add_aloe_options(self, parser):
        """Add Aloe options to the parser."""

        parser.add_argument(
            '--test-class', action='store',
            dest='test_class_name',
            default=self.test_class_name,
            metavar='TEST_CLASS',
            help='Base class to use for the generated tests',
        )
        parser.add_argument(
            '--no-ignore-python', action='store_false',
            dest='ignore_python',
            default=self.ignore_python,
            help='Run Python and Gherkin tests together',
        )
        parser.add_argument(
            '-n', '--scenario-indices', action='store',
            dest='scenario_indices',
            default=self.scenario_indices,
            help='Only run scenarios with these indices (comma-separated)',
        )
        parser.add_argument(
            '--progress', action='store_const',
            dest='verbosity', const=3,
            help='Show the progress of running scenarios',
        )
        parser.add_argument(
            '--color', action='store_true',
            dest='force_color',
            default=self.force_color,
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

    def _getParentArgParser(self):  # pylint:disable=invalid-name
        """Add arguments specific to Aloe."""

        parser = super()._getParentArgParser()  # pylint:disable=no-member
        self.add_aloe_options(parser)
        return parser

    def createTests(self):
        """Set up loader before running tests."""

        self.setup_loader()

        return super().createTests()

    def _do_discovery(self, argv, Loader=None):
        """Set up loader before running discovery."""

        if PY2:
            parser = argparse.ArgumentParser(add_help=False)
            self.add_aloe_options(parser)
            _, argv = parser.parse_known_args(argv, self)

        return super()._do_discovery(argv, Loader=self.setup_loader)

    def setup_loader(self):
        """Pass extra options to the test loader."""

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

        return self.testLoader

    def runTests(self):
        """Run the "all" level callbacks."""

        # Loader is really GherkinLoader
        # pylint:disable=no-member
        self.testLoader.run_before_callbacks()
        super().runTests()
        self.testLoader.run_after_callbacks()
