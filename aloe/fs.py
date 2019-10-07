# -*- coding: utf-8 -*-
"""
Filesystem-related utilities.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import fnmatch

from future.utils import raise_from

from nose.importer import Importer

from aloe.exceptions import StepDiscoveryError


GHERKIN_FEATURES_DIR_NAME = 'GHERKIN_FEATURES_DIR_NAME'


def path_to_module_name(filename):
    """Convert a path to a file to a Python module name."""

    filename = os.path.relpath(filename)

    dotted_path = []
    while True:
        filename, component = os.path.split(filename)
        dotted_path.insert(0, component)
        if filename == '':
            break

    dotted_path[-1] = os.path.splitext(dotted_path[-1])[0]
    if dotted_path[-1] == '__init__':
        dotted_path.pop()

    return '.'.join(dotted_path)


class FeatureLoader(object):
    """Loader class responsible for findind features and step
    definitions along a given path on filesystem"""

    importer = Importer()

    @classmethod
    def find_and_load_step_definitions(cls, dir_):
        """
        Load the steps from the specified directory.
        """

        for path, _, files in os.walk(dir_):
            for filename in fnmatch.filter(files, '*.py'):
                # Import the module using its fully qualified name
                filename = os.path.relpath(os.path.join(path, filename))
                module_name = path_to_module_name(filename)

                try:
                    cls.importer.importFromPath(filename, module_name)
                except ImportError as exc:
                    raise_from(
                        StepDiscoveryError(
                            "Cannot load step definition file: '%s'" % filename
                        ),
                        exc
                    )

    @classmethod
    def features_dirname(cls):
        """
        Set the name of the features directory.
        It is possible to change the name by setting the environment variable:
        GHERKIN_FEATURES_DIR_NAME = 'gherkin_features'
        """

        env = os.environ
        features_dirname = env.get(GHERKIN_FEATURES_DIR_NAME, 'features')

        # check the dir name is not a path
        if '/' in features_dirname:
            raise_from(
                StepDiscoveryError("%s cannot be a path: %s" % (
                    GHERKIN_FEATURES_DIR_NAME, features_dirname)),
                None
            )

        return features_dirname

    @classmethod
    def find_feature_directories(cls, dir_):
        """
        Locate directories to load features from.

        The directories should be named 'features'; they must either reside
        directly in the specified directory, or otherwise all their parents
        must be packages (have __init__.py files).
        """

        features_dirname = cls.features_dirname()

        # A set of package directories discovered
        packages = set()

        for path, dirs, files in os.walk(dir_, followlinks=True):
            # Is this a package?
            if '__init__.py' in files:
                packages.add(path)

            if path == dir_ or path in packages:
                # Does this package have a feature directory?
                if features_dirname in dirs:
                    yield os.path.join(path, features_dirname)

            else:
                # This is not a package, prune search
                dirs[:] = []
