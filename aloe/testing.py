# Aloe - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Utilities for testing libraries using Aloe.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin
standard_library.install_aliases()

import os
import sys
import tempfile
import unittest
from functools import wraps

from aloe import world
from aloe.fs import path_to_module_name
from aloe.plugin import GherkinPlugin
from aloe.registry import (
    CALLBACK_REGISTRY,
    PriorityClass,
    STEP_REGISTRY,
)
from aloe.runner import Runner


def in_directory(directory):
    """
    A decorator to change the current directory and add the new one to the
    Python module search path.

    Upon exiting, the directory is changed back, the module search path change
    is reversed and all modules loaded from the directory are removed from
    sys.modules.

    Applies to either a function or an instance of
    TestCase, in which case setUp/tearDown are used.
    """

    directory = os.path.abspath(directory)
    last_wd = [None]

    def apply_directory():
        """
        Change the directory and put it onto the module search path.
        """

        last_wd[0] = os.getcwd()
        sys.path.insert(0, directory)
        os.chdir(directory)

    def unapply_directory():
        """
        Undo the directory and module search path change.
        """

        os.chdir(last_wd[0])
        sys.path.remove(directory)
        last_wd[0] = None

        # Unload modules which are loaded from the directory
        unload_modules = []
        unload_path_prefix = os.path.join(directory, '')
        for module_name, module in sys.modules.items():
            # Find out where is the module loaded from
            try:
                path = module.__file__
            except AttributeError:
                # Maybe a namespace package module?
                try:
                    if module.__spec__.origin == 'namespace':
                        path = module.__path__._path[0]
                    else:
                        continue
                except AttributeError:
                    continue

            # Is it loaded from a file in the directory?
            path = os.path.abspath(path)
            if not path.startswith(unload_path_prefix):
                continue

            # Does its name match what would it be if it was? Consider two
            # directories, foo/ and foo/bar on sys.path, foo/bar/baz.py might
            # have been loaded from either.
            path = path[len(unload_path_prefix):]
            if module_name == path_to_module_name(path):
                unload_modules.append(module_name)

        for module in unload_modules:
            del sys.modules[module]

    def wrapper(func_or_class):
        """
        Wrap a function or a test case class to execute in a different
        directory.
        """

        try:
            is_test_case = issubclass(func_or_class, unittest.TestCase)
        except TypeError:
            is_test_case = False

        if is_test_case:
            # Wrap setUp/tearDown
            old_setup = func_or_class.setUp
            old_teardown = func_or_class.tearDown

            @wraps(old_setup)
            def setUp(self):
                """Wrap setUp to change to given directory first."""
                apply_directory()
                old_setup(self)

            @wraps(old_teardown)
            def tearDown(self):
                """Wrap tearDown to restore the original directory."""
                old_teardown(self)
                unapply_directory()

            func_or_class.setUp = setUp
            func_or_class.tearDown = tearDown

            return func_or_class

        else:
            # Wrap a function
            @wraps(func_or_class)
            def wrapped(*args, **kwargs):
                """
                Execute the function in a different directory.
                """

                apply_directory()
                try:
                    return func_or_class(*args, **kwargs)
                finally:
                    unapply_directory()

            return wrapped

    return wrapper


class TestGherkinPlugin(GherkinPlugin):
    """
    Test Gherkin plugin.
    """

    def loadTestsFromFile(self, file_):
        """
        Record which tests were run.
        """

        for scenario in super().loadTestsFromFile(file_):
            yield scenario

        self.runner.tests_run.append(file_)


class TestRunner(Runner):
    """
    A test test runner to store information about the tests run.
    """

    def gherkin_plugin(self):
        """
        Override the plugin class.
        """

        plugin = TestGherkinPlugin()
        plugin.runner = self
        return plugin

    def __init__(self, *args, **kwargs):
        self.tests_run = []
        super().__init__(*args, **kwargs)


class FeatureTest(unittest.TestCase):
    """
    Base class for tests running Gherkin features.
    """

    def setUp(self):
        """
        Ensure inner Nose doesn't redirect output.
        """

        os.environ['NOSE_NOCAPTURE'] = '1'

    def run_feature_string(self, feature_string):
        """
        Run the specified string as a feature.
        """

        with tempfile.NamedTemporaryFile(suffix='.feature', dir=os.getcwd()) \
                as feature_file:
            feature_file.write(feature_string.encode())
            feature_file.flush()
            return self.run_features(os.path.relpath(feature_file.name))

    def run_features(self, *features):
        """
        Run the specified features.
        """

        CALLBACK_REGISTRY.clear(priority_class=PriorityClass.USER)
        STEP_REGISTRY.clear()
        world.__dict__.clear()

        return TestRunner(exit=False,
                          argv=['aloe'] + list(features))

    def assert_feature_success(self, *features):
        """
        Assert that the specified features can be run successfully.
        """

        result = self.run_features(*features)
        assert result.success
        return result

    def assert_feature_fail(self, *features):
        """
        Assert that the specified features fail when run.
        """

        result = self.run_features(*features)
        assert not result.success
        return result
