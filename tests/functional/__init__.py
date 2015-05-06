# Lychee - Cucumber runner for Python based on Lettuce and Nose
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
Common utilities for functional tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from builtins import super
standard_library.install_aliases()

import os
import unittest
from functools import wraps

from lychee import world
from lychee.plugin import GherkinPlugin
from lychee.registry import (
    clear as clear_registry,
    PriorityClass,
)
from lychee.runner import Runner


def in_directory(directory):
    """
    A decorator to change the current directory.
    """

    def wrapper(func_or_class):
        """
        Wrap a function or a test case class to execute in a different
        directory.
        """

        if issubclass(func_or_class, unittest.TestCase):
            # Wrap setUp/tearDown
            old_setup = func_or_class.setUp
            old_teardown = func_or_class.tearDown

            @wraps(old_setup)
            def setUp(self):
                self._last_wd = os.getcwd()
                os.chdir(directory)
                old_setup(self)

            @wraps(old_teardown)
            def tearDown(self):
                old_teardown(self)
                os.chdir(self._last_wd)
                delattr(self, '_last_wd')

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

                cwd = os.getcwd()
                os.chdir(directory)
                try:
                    return func_or_class(*args, **kwargs)
                finally:
                    os.chdir(cwd)

            return wrapped

    return wrapper


class TestGherkinPlugin(GherkinPlugin):
    """
    Test Gherkin plugin.
    """

    def loadTestsFromFile(self, file):
        """
        Record which tests were run.
        """

        for scenario in super().loadTestsFromFile(file):
            yield scenario

        self.runner.tests_run.append(file)


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

    def run_features(self, *features):
        """
        Run the specified features.
        """

        clear_registry(priority_class=PriorityClass.USER)
        world.__dict__.clear()

        return TestRunner(exit=False,
                          argv=['lychee'] + list(features))

    def assert_feature_success(self, *features):
        """
        Assert that the specified features can be run successfully.
        """

        result = self.run_features(*features)
        assert result.success

    def assert_feature_fail(self, *features):
        """
        Assert that the specified features fail when run.
        """

        result = self.run_features(*features)
        assert not result.success
