import os

from nose.plugins import Plugin


class GherkinPlugin(Plugin):
    """
    Collect Gherkin tests.
    """

    name = 'gherkin'

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

        raise NotImplementedError
