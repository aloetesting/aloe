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
Gherkin plugin for Nose.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()

import os

from nose.plugins import Plugin

from lychee.fs import FeatureLoader
from lychee.testclass import TestCase


class GherkinPlugin(Plugin):
    """
    Collect Gherkin tests.
    """

    name = 'gherkin'
    enableOpt = 'gherkin'

    TEST_CLASS = TestCase

    def begin(self):
        """
        Load the steps.
        """

        loader = FeatureLoader('.')
        loader.find_and_load_step_definitions()

    def options(self, parser, env=os.environ):
        """
        Register the plugin options.
        """

        super().options(parser, env)

        test_class_name = \
            '{c.__module__}.{c.__name__}'.format(c=self.TEST_CLASS)
        parser.add_option(
            '--test-class', action='store',
            dest='test_class_name',
            default=env.get('NOSE_GHERKIN_CLASS', test_class_name),
            metavar='TEST_CLASS',
            help='Base class to use for the generated tests.',
        )

    def configure(self, options, conf):
        """
        Configure the plugin.
        """

        super().configure(options, conf)

        module_name, class_name = options.test_class_name.rsplit('.', 1)
        module = __import__(module_name, fromlist=(class_name,))
        self.test_class = getattr(module, class_name)

    def wantDirectory(self, directory):
        """
        Collect features from 'features' directories.
        """

        if os.path.basename(directory) == 'features':
            return True

    def wantFile(self, file):
        """
        Load features from feature files.
        """

        if os.path.basename(file).endswith('.feature'):
            return True

    def loadTestsFromFile(self, file):
        """
        Load a feature from the feature file.
        """

        test = self.test_class.from_file(file)
        for method in test.__dict__:
            if getattr(getattr(test, method), 'is_scenario', False):
                yield test(method)
