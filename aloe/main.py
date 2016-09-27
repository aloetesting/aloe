"""
Unittest main working with Gherkin tests.
"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin

import argparse
import os
import unittest

from aloe.loader import GherkinLoader
from aloe.runner import GherkinRunner
from aloe.testclass import TestCase
from aloe.utils import callable_type, module_attribute, PY2


def test_class_name(test_class):
    """The test class name, possibly overridden by GHERKIN_TEST_CLASS."""
    if 'GHERKIN_TEST_CLASS' in os.environ:
        return os.environ['GHERKIN_TEST_CLASS']
    else:
        return '{c.__module__}.{c.__name__}'.format(c=test_class)


class AloeOptions(object):
    """A mixin for parsing Aloe-specific options and passing them through."""

    # Options set by parsing arguments
    test_class = TestCase
    force_color = False
    ignore_python = True
    scenario_indices = ''
    tags = []
    exclude_tags = []

    @classmethod
    def add_aloe_options(cls, parser):
        """Add Aloe options to the parser."""

        parser.add_argument(
            '--test-class', action='store',
            dest='test_class',
            default=test_class_name(cls.test_class),
            type=module_attribute,
            metavar='TEST_CLASS',
            help='Base class to use for the generated tests',
        )
        parser.add_argument(
            '--no-ignore-python', action='store_false',
            dest='ignore_python',
            default=cls.ignore_python,
            help='Run Python and Gherkin tests together',
        )
        parser.add_argument(
            '-n', '--scenario-indices', action='store',
            dest='scenario_indices',
            default=cls.scenario_indices,
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
            default=cls.force_color,
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

    def configure_loader(self, test_loader):
        """
        Pass extra options to the test loader.

        The options are assumed to have been put onto self by parsing the
        arguments in add_aloe_options.
        """

        test_loader.force_color = self.force_color
        test_loader.ignore_python = self.ignore_python

        if self.scenario_indices:
            test_loader.scenario_indices = tuple(
                int(index)
                for index in self.scenario_indices.split(',')
            )
        else:
            test_loader.scenario_indices = None

        test_loader.test_class = self.test_class

        test_loader.tags = set(self.tags or ())
        test_loader.exclude_tags = set(self.exclude_tags or ())

    def extra_runner_args(self):
        """Extra arguments to pass to the test runner."""

        return {
            'force_color': self.force_color,
        }


class TestProgram(AloeOptions, unittest.TestProgram):
    """
    A test program loading Gherkin tests.
    """

    gherkin_loader = GherkinLoader

    def __init__(self, *args, **kwargs):
        """
        Enable Gherkin loading plugins and run the tests.
        """

        kwargs.setdefault('testLoader', self.gherkin_loader())
        kwargs.setdefault('testRunner', callable_type(self.make_runner))
        super().__init__(*args, **kwargs)

    def make_runner(self, *args, **kwargs):
        """Pass extra arguments to the test runner."""
        kwargs.update(self.extra_runner_args())
        return GherkinRunner(*args, **kwargs)

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

        self.configure_loader(self.testLoader)
        return self.testLoader
