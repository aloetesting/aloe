"""
Nose test runner with Gherkin plugin enabled.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin

import os

import nose.core

from aloe.plugin import GherkinPlugin


class Runner(nose.core.TestProgram):
    """
    A test runner collecting Gherkin tests.
    """

    def gherkin_plugin(self):
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
