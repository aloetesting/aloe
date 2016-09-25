"""
Loader for tests written in Gherkin.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin,wildcard-import,unused-wildcard-import
from builtins import *
# pylint:enable=redefined-builtin,wildcard-import,unused-wildcard-import

import fnmatch
import itertools
import os
import unittest

from aloe.exceptions import AloeSyntaxError
from aloe.fs import FeatureLoader
from aloe.registry import CALLBACK_REGISTRY
from aloe.utils import identifier


def _make_failed_test(exception):
    """Make a test that raises an exception."""

    def test_failure(self):
        """Raise the exception."""
        raise exception

    attrs = {'test_failure': test_failure}
    test_class = type(identifier('AloeFailedTest'), (unittest.TestCase,), attrs)
    return test_class('test_failure')


class GherkinLoader(unittest.loader.TestLoader):
    """
    Collect Gherkin tests.
    """

    def __init__(self):
        """Initialise the Gherkin loader."""

        super().__init__()

        # Will be set by the main test program
        self.ignore_python = True
        self.scenario_indices = None
        self.tags = None
        self.exclude_tags = None

        self.steps_loaded = False

    def load_steps(self):
        """Discover feature directories and load the step definitions."""

        if self.steps_loaded:
            return

        self.feature_dirs = [
            dir_
            for dir_ in FeatureLoader.find_feature_directories('.')
        ]
        for feature_dir in self.feature_dirs:
            FeatureLoader.find_and_load_step_definitions(feature_dir)

        self.steps_loaded = True

    def discover(self, start_dir, pattern=None, top_level_dir=None):
        """Discover all features in feature directories."""

        self.load_steps()

        # tests is an iterable, Pylint warns about generator/chain
        # pylint:disable=redefined-variable-type
        tests = self.tests_from_directory(start_dir)

        if not self.ignore_python:
            python_tests = super().discover(start_dir, pattern=pattern,
                                            top_level_dir=top_level_dir)
            tests = itertools.chain(tests, python_tests)

        return self.suiteClass(tests)

    def loadTestsFromName(self, name, module=None):
        """Load features from a file or a directory containing them."""

        self.load_steps()

        # tests is an iterable, Pylint warns about generator/list/chain
        # pylint:disable=redefined-variable-type
        if os.path.isdir(name):
            tests = self.tests_from_directory(name)
        elif os.path.isfile(name):
            tests = self.tests_from_file(name)
        else:
            tests = []

        if not self.ignore_python:
            python_tests = super().loadTestsFromName(name, module=module)
            tests = itertools.chain(tests, python_tests)

        return self.suiteClass(tests)

    def is_feature_directory(self, directory):
        """
        Whether to collect features from a directory.

        This returns true for any directory _below_ any of
        the features directories to ensure features from all the
        subdirectories are collected.
        """

        directory = os.path.abspath(directory)
        for feature_dir in self.feature_dirs:
            feature_dir = os.path.abspath(feature_dir)
            if directory.startswith(feature_dir):
                return True

    def scenario_matches(self, feature, scenario_index, scenario_name):
        """
        Whether a given scenario is selected by the command-line options.

        @feature The feature class
        @scenario_index The scenario index
        @scenario_name The scenario name
        """

        # pylint:disable=unsupported-membership-test
        # scenario_indices is either None or an iterable
        if self.scenario_indices:
            if scenario_index not in self.scenario_indices:
                return False

        scenario = getattr(feature, scenario_name)
        tags = getattr(scenario, 'tags', set())
        if self.tags and not tags & self.tags:
            return False
        if self.exclude_tags and tags & self.exclude_tags:
            return False

        return True

    def tests_from_file(self, file_):
        """
        Load a feature from the feature file and return an iterable of the
        tests contained.
        """

        try:
            # pylint:disable=no-member
            # test_class is set by AloeOptions
            test = self.test_class.from_file(file_)
        except AloeSyntaxError as exc:
            yield _make_failed_test(exc)
            return

        # About to run a feature - ensure "before all" callbacks have run
        self.run_before_callbacks()

        # Filter the scenarios, if asked
        for idx, scenario_name in test.scenarios():
            if self.scenario_matches(test, idx, scenario_name):
                yield test(scenario_name)

    def tests_from_directory(self, directory):
        """
        Load all tests from all features from within the specified directory.
        """

        features = sorted(self.find_features(directory))
        for feature in features:
            for test in self.tests_from_file(feature):
                yield test

    def find_features(self, directory):
        """
        An iterable of all the feature files within a specified directory.
        """

        for path, _, files in os.walk(directory, followlinks=True):
            if self.is_feature_directory(path):
                for filename in fnmatch.filter(files, '*.feature'):
                    yield os.path.join(path, filename)

    def run_before_callbacks(self):
        """Run the "before all" callbacks."""

        if not hasattr(self, 'after_hook'):
            before_all, after_all = CALLBACK_REGISTRY.before_after('all')
            before_all()
            self.after_hook = after_all

    def run_after_callbacks(self):
        """Run the "after all" callbacks."""

        if hasattr(self, 'after_hook'):
            self.after_hook()
            delattr(self, 'after_hook')
