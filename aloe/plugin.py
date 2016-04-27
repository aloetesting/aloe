"""
Gherkin plugins for various testing frameworks.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin,wildcard-import,unused-wildcard-import
from builtins import *
# pylint:enable=redefined-builtin,wildcard-import,unused-wildcard-import

import sys
import os

from importlib import import_module

from aloe.fs import FeatureLoader
from aloe.registry import CALLBACK_REGISTRY
from aloe.testclass import TestCase


class GherkinPluginBase(object):
    """
    Base for different test frameworks' plugins.

    This class only contains methods that are used by the concrete plugin
    implementations.
    """

    TEST_CLASS = TestCase

    def find_features_steps(self):
        """Find the feature and step definitions."""

        self.feature_dirs = [
            dir_
            for dir_ in FeatureLoader.find_feature_directories('.')
        ]
        for feature_dir in self.feature_dirs:
            FeatureLoader.find_and_load_step_definitions(feature_dir)

    def set_configuration(self, options):
        """Configure the plugin based on the configuration object."""

        module_name, class_name = options.test_class_name.rsplit('.', 1)
        module = import_module(module_name)
        self.test_class = getattr(module, class_name)
        self.ignore_python = options.ignore_python

        if options.scenario_indices:
            self.scenario_indices = tuple(
                int(index)
                for index in options.scenario_indices.split(',')
            )
        else:
            self.scenario_indices = None

    def consider_directory(self, directory):
        """
        Whether a directory should be considered when looking for feature files.

        This returns true for any directory either _above_ or _below_ any of
        the features directories; above to ensure the search continues inside,
        below to collect features from all the subdirectories.
        """

        directory = os.path.abspath(directory)
        for feature_dir in self.feature_dirs:
            feature_dir = os.path.abspath(feature_dir)
            if feature_dir.startswith(directory) or \
                    directory.startswith(feature_dir):
                return True

        return False

    def is_feature_file(self, file_):
        """Whether a file is a feature file to be loaded."""

        # Check that the feature is in one of the features directories
        file_dir = os.path.abspath(os.path.dirname(file_))
        if any(
                file_dir.startswith(os.path.abspath(feature_dir))
                for feature_dir in self.feature_dirs
        ):
            # Check the file extension
            # Convert to str (not bytes) since Nose passes in both depending on
            # whether the feature is in a Python module dir or not
            if isinstance(file_, bytes):
                file_ = file_.decode(sys.getfilesystemencoding())
            if os.path.basename(file_).endswith('.feature'):
                return True

        return False

    def scenario_matches(self, feature, scenario_index, scenario_name):
        """
        Whether a given scenario is selected by the command-line options.

        :param feature: The feature class
        :param scenario_index: The scenario index
        :param scenario_name: The scenario name
        """

        if self.scenario_indices:
            if scenario_index not in self.scenario_indices:
                return False

        return True

    def ensure_before_callbacks(self):
        """Ensure the "before all" callbacks have run."""

        if not hasattr(self, 'after_hook'):
            before_all, after_all = CALLBACK_REGISTRY.before_after('all')
            before_all()
            self.after_hook = after_all

    def ensure_after_callbacks(self):
        """Ensure the "after all" callbacks have run."""

        if hasattr(self, 'after_hook'):
            self.after_hook()
            delattr(self, 'after_hook')
