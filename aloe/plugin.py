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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin
from future import standard_library
standard_library.install_aliases()

import os

from importlib import import_module

from nose.plugins import Plugin

from aloe.fs import FeatureLoader
from aloe.registry import CALLBACK_REGISTRY
from aloe.testclass import TestCase


class GherkinPlugin(Plugin):
    """
    Collect Gherkin tests.
    """

    # Nose interface has non-Pythonic names
    # pylint:disable=invalid-name,unused-argument

    name = 'gherkin'
    enableOpt = 'gherkin'

    TEST_CLASS = TestCase

    def begin(self):
        """
        Start the test suite, resetting internal state.
        """

        self.steps_loaded = []
        self.context_level = 0

    def options(self, parser, env=None):
        """
        Register the plugin options.
        """

        if env is None:
            env = os.environ

        super().options(parser, env)

        test_class_name = \
            '{c.__module__}.{c.__name__}'.format(c=self.TEST_CLASS)
        parser.add_option(
            '--test-class', action='store',
            dest='test_class_name',
            default=env.get('NOSE_GHERKIN_CLASS', test_class_name),
            metavar='TEST_CLASS',
            help='Base class to use for the generated tests',
        )
        parser.add_option(
            '--no-ignore-python', action='store_false',
            dest='ignore_python',
            default=True,
            help='Run Python and Gherkin tests together',
        )
        parser.add_option(
            '-n', '--scenario-indices', action='store',
            dest='scenario_indices',
            default='',
            help='Only run scenarios with these indices (comma-separated)',
        )

    def configure(self, options, conf):
        """
        Configure the plugin.
        """

        super().configure(options, conf)

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

    def wantDirectory(self, directory):
        """
        Collect features from 'features' directories.
        """

        directory = os.path.abspath(directory)
        while directory != '/':
            if os.path.basename(directory) == 'features':
                return True
            directory = os.path.dirname(directory)

    def wantFile(self, file):
        """
        Load features from feature files.
        """

        if os.path.basename(file).endswith('.feature'):
            return True

    def wantPython(self, _):
        """
        Ignore Python tests if required.
        """

        if self.ignore_python:
            return False

    wantClass = wantFunction = wantMethod = wantModule = wantPython

    def loadTestsFromFile(self, file):
        """
        Load a feature from the feature file.
        """

        # Ensure the steps corresponding to the feature file are loaded
        steps_dir = FeatureLoader.find_steps_dir(file)
        if steps_dir not in self.steps_loaded:
            FeatureLoader.find_and_load_step_definitions(steps_dir)
            self.steps_loaded.append(steps_dir)

        test = self.test_class.from_file(file)

        # Filter the scenarios, if asked
        for scenario_index, scenario_name in test.scenarios():
            if not self.scenario_indices or \
                    scenario_index in self.scenario_indices:
                yield test(scenario_name)

    def startContext(self, context):
        """
        On the first context, run the "before all" callbacks.
        """

        # TODO: Is there a better method to do something before _and after_ all
        # the tests have been run?

        if self.context_level == 0:
            before_all, after_all = CALLBACK_REGISTRY.before_after('all')
            before_all()
            self.after_hook = after_all

        self.context_level += 1

    def stopContext(self, context):
        """
        On the last context, run the "after all" callbacks.
        """

        self.context_level -= 1

        if self.context_level == 0:
            self.after_hook()
            delattr(self, 'after_hook')
