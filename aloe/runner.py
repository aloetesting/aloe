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
from builtins import super
from future import standard_library
standard_library.install_aliases()

import os

import nose.core

from aloe.plugin import GherkinPlugin


class Runner(nose.core.TestProgram):
    """
    A test runner collecting Gherkin tests.
    """

    @staticmethod
    def gherkin_plugin():
        """
        The plugin to add to the runner.
        Hook point for tests.
        """

        return GherkinPlugin()

    def __init__(self, *args, **kwargs):
        """
        Enable Gherkin loading plugins and run the tests.
        """

        # Add Gherkin plugin
        kwargs.setdefault('addplugins', []).append(self.gherkin_plugin())

        # Ensure it's loaded
        env = kwargs.pop('env', os.environ)
        env['NOSE_WITH_GHERKIN'] = '1'
        kwargs['env'] = env

        super().__init__(*args, **kwargs)
