import os

import nose.core

from lychee.plugin import GherkinPlugin


class Runner(nose.core.TestProgram):
    """
    A test runner collecting Gherkin tests.
    """

    def __init__(self, *args, **kwargs):
        """
        Enable Gherkin loading plugins and run the tests.
        """

        # Add Gherkin plugin
        kwargs.setdefault('addplugins', []).append(GherkinPlugin())

        # Ensure it's loaded
        env = kwargs.pop('env', os.environ)
        env['NOSE_WITH_GHERKIN'] = '1'
        kwargs['env'] = env

        super().__init__(*args, **kwargs)
