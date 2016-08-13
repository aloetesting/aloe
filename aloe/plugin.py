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
        raise NotImplementedError("Discovery not implemented")

    def loadTestsFromName(self, name, module=None):
        if isinstance(name, str):
            return self.suiteClass(self.tests_from(name))
        raise NotImplementedError

    def loadTestsFromModule(self, module, *args, pattern=None, **kws):
        raise NotImplementedError

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

    def tests_from(self, file_or_dir):
        """
        Load a feature from the feature file and return an iterable of the
        tests contained.
        """

        if os.path.isdir(file_or_dir):
            for path, _, files in os.walk(file_or_dir):
                if self.is_feature_directory(path):
                    for filename in fnmatch.filter(files, '*.feature'):
                        filepath = os.path.join(path, filename)
                        for test in self.tests_from(filepath):
                            yield test
            return

        test = self.test_class.from_file(file_or_dir)

        # About to run a feature - ensure "before all" callbacks have run
        self.ensure_before_callbacks()

        # Filter the scenarios, if asked
        for idx, scenario_name in test.scenarios():
            if self.scenario_matches(test, idx, scenario_name):
                yield test(scenario_name)

    def ensure_before_callbacks(self):
        """
        Before the first test, run the "before all" callbacks.
        """

        if not hasattr(self, 'after_hook'):
            before_all, after_all = CALLBACK_REGISTRY.before_after('all')
            before_all()
            self.after_hook = after_all

    def finalize(self, result):
        """
        After the last test, run the "after all" callbacks.
        """

        # TODO: Is there a better method to do something _after_ all the tests
        # have been run?

        if hasattr(self, 'after_hook'):
            self.after_hook()
            delattr(self, 'after_hook')
