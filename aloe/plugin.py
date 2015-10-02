"""
Gherkin plugin for Nose.
"""

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
from nose.plugins.attrib import AttributeSelector

from aloe.fs import FeatureLoader
from aloe.registry import CALLBACK_REGISTRY
from aloe.testclass import TestCase
from aloe.result import AloeTestResult


class GherkinPlugin(Plugin):
    """
    Collect Gherkin tests.
    """

    # Nose interface has non-Pythonic names
    # pylint:disable=invalid-name,unused-argument

    name = 'gherkin'
    enableOpt = 'gherkin'

    TEST_CLASS = TestCase

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

        self.feature_dirs = [
            dir_
            for dir_ in FeatureLoader.find_feature_directories('.')
        ]
        for feature_dir in self.feature_dirs:
            FeatureLoader.find_and_load_step_definitions(feature_dir)

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

        module_name, class_name = options.test_class_name.rsplit('.', 1)
        module = import_module(module_name)
        self.test_class = getattr(module, class_name)
        self.ignore_python = options.ignore_python

        conf.force_color = options.force_color

        if options.scenario_indices:
            self.scenario_indices = tuple(
                int(index)
                for index in options.scenario_indices.split(',')
            )
        else:
            self.scenario_indices = None

        self.attrib_plugin.configure(options, conf)

    def wantDirectory(self, directory):
        """
        Collect features from 'features' directories.

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

    def wantFile(self, file_):
        """
        Load features from feature files.
        """

        # Check that the feature is in one of the features directories
        file_dir = os.path.abspath(os.path.dirname(file_))
        if any(
                file_dir.startswith(os.path.abspath(feature_dir))
                for feature_dir in self.feature_dirs
        ) and os.path.basename(file_).endswith('.feature'):
            return True

    def wantPython(self, _):
        """
        Ignore Python tests if required.
        """

        if self.ignore_python:
            return False

    wantClass = wantFunction = wantMethod = wantModule = wantPython

    def scenario_matches(self, feature, scenario_index, scenario_name):
        """
        Whether a given scenario is selected by the command-line options.

        @feature The feature class
        @scenario_index The scenario index
        @scenario_name The scenario name
        """

        if self.scenario_indices:
            if scenario_index not in self.scenario_indices:
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

    def ensure_before_callbacks(self):
        """
        Before the first test, run the "before all" callbacks.
        """

        if not hasattr(self, 'after_hook'):
            before_all, after_all = CALLBACK_REGISTRY.before_after('all')
            before_all()
            self.after_hook = after_all

    def finalize(self, result):
        """
        After the last test, run the "after all" callbacks.
        """

        # TODO: Is there a better method to do something _after_ all the tests
        # have been run?

        if hasattr(self, 'after_hook'):
            self.after_hook()
            delattr(self, 'after_hook')

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
