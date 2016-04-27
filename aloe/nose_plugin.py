"""
Gherkin plugin for Nose.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin,wildcard-import,unused-wildcard-import
from builtins import *
# pylint:enable=redefined-builtin,wildcard-import,unused-wildcard-import

import os

import nose.core
from nose.plugins import Plugin
from nose.plugins.attrib import AttributeSelector

from aloe.plugin import GherkinPluginBase
from aloe.result import AloeTestResult


class GherkinPlugin(GherkinPluginBase, Plugin):
    """
    Gherkin plugin for Nose.
    """

    # Nose interface has non-Pythonic names
    # pylint:disable=invalid-name,unused-argument

    name = 'gherkin'
    enableOpt = 'gherkin'

    def __init__(self):
        """Initialise the helper plugin."""

        # Nose has attrib plugin which works as expected but isn't passed the
        # tests generated from features. Create a local copy which will be used
        # to veto the tests.

        super().__init__()
        self.attrib_plugin = AttributeSelector()

    def begin(self):
        """
        Start the test suite, loading all the step definitions.
        """

        if self.conf.options.version or self.conf.options.showPlugins:
            # Don't try to load anything if only called for information
            return

        self.find_features_steps()

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
        parser.add_option(
            '--color', action='store_true',
            dest='force_color',
            default=False,
            help='Force colored output',
        )

        # Options for attribute plugin will be registered by its main instance

    def configure(self, options, conf):
        """
        Configure the plugin.
        """

        super().configure(options, conf)

        self.set_configuration(options)

        conf.force_color = options.force_color

        self.attrib_plugin.configure(options, conf)

    def wantDirectory(self, directory):
        """Whether to look for feature files in a directory."""
        if self.consider_directory(directory):
            return True

    def wantFile(self, file_):
        """Whether to load a file as a feature file."""
        if self.is_feature_file(file_):
            return True

    def wantPython(self, _):
        """
        Ignore Python tests if required.
        """

        if self.ignore_python:
            return False

    wantClass = wantFunction = wantMethod = wantModule = wantPython

    def scenario_matches(self, feature, scenario_index, scenario_name):
        if not super().scenario_matches(feature, scenario_index, scenario_name):
            return False

        if self.attrib_plugin.enabled:
            scenario = getattr(feature, scenario_name)
            # False means "no", None means "don't care" for Nose plugins
            if self.attrib_plugin.validateAttrib(scenario, feature) is False:
                return False

        return True

    def loadTestsFromFile(self, file_):
        """
        Load a feature from the feature file.
        """

        test = self.test_class.from_file(file_)

        # About to run a feature - ensure "before all" callbacks have run
        self.ensure_before_callbacks()

        has_tests = False

        # Filter the scenarios, if asked
        for idx, scenario_name in test.scenarios():
            if self.scenario_matches(test, idx, scenario_name):
                has_tests = True
                yield test(scenario_name)

        # Feature OK but no tests filtered
        if not has_tests:
            yield False

    def finalize(self, result):
        """
        After the last test, run the "after all" callbacks.
        """

        # TODO: Is there a better method to do something _after_ all the tests
        # have been run?

        self.ensure_after_callbacks()

    def prepareTestRunner(self, runner):
        """
        Monkeypatch in our TestResult class.

        In unittest we could just set runner.resultclass, but Nose
        doesn't use this.
        """
        def _makeResult():
            """Build our result"""
            return AloeTestResult(runner.stream,
                                  runner.descriptions,
                                  runner.verbosity,
                                  runner.config)

        runner._makeResult = _makeResult  # pylint:disable=protected-access

        return runner


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
