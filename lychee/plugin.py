import os

from nose.plugins import Plugin

from lychee.testclass import TestCase


class GherkinPlugin(Plugin):
    """
    Collect Gherkin tests.
    """

    name = 'gherkin'

    TEST_CLASS = TestCase

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
        return self.TEST_CLASS.from_file(file)
