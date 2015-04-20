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

import os

from nose.plugins import Plugin

from lychee.fs import FeatureLoader
from lychee.testclass import TestCase


class GherkinPlugin(Plugin):
    """
    Collect Gherkin tests.
    """

    name = 'gherkin'

    TEST_CLASS = TestCase

    def begin(self):
        """
        Load the steps.
        """

        loader = FeatureLoader('.')
        loader.find_and_load_step_definitions()

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

        # TODO: How to customize the test class?
        test = self.TEST_CLASS.from_file(file)
        for method in test.__dict__:
            if getattr(getattr(test, method), 'is_scenario', False):
                yield test(method)
