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

from aloe.fs import FeatureLoader
from aloe.registry import CALLBACK_REGISTRY


class GherkinLoader(unittest.loader.TestLoader):
    """
    Collect Gherkin tests.
    """

    def __init__(self):
        """Initialise the helper plugin."""

        super().__init__()

        # Will be set by the main test program
        self.scenario_indices = None
        self.tags = None
        self.exclude_tags = None

        # Load all the step definitions
        self.feature_dirs = [
            dir_
            for dir_ in FeatureLoader.find_feature_directories('.')
        ]
        for feature_dir in self.feature_dirs:
            FeatureLoader.find_and_load_step_definitions(feature_dir)

    def discover(self, start_dir, pattern=None, top_level_dir=None):
        """Discover all features in feature directories."""

        tests = itertools.chain.from_iterable(
            self.tests_from_directory(feature_dir)
            for feature_dir in self.feature_dirs
        )
        return self.suiteClass(tests)

    def loadTestsFromName(self, name, module=None):
        """Load features from a file or a directory containing them."""
        if isinstance(name, str):
            if os.path.isdir(name):
                tests = self.tests_from_directory(name)
            else:
                tests = self.tests_from_file(name)
            return self.suiteClass(tests)
        raise NotImplementedError

    def loadTestsFromModule(self, *args, **kwargs):
        """Ignore Python tests."""
        return self.suiteClass([])

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

        test = self.test_class.from_file(file_)

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

        for path, _, files in os.walk(directory):
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
