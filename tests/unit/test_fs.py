"""
Test filesystem-related functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import unittest

from aloe.exceptions import StepDiscoveryError
from aloe.fs import FeatureLoader, path_to_module_name


class PathToModuleNameTest(unittest.TestCase):
    """
    Test path_to_module_name.
    """

    def test_path_to_module_name(self):
        """Test path_to_module_name."""

        self.assertEqual(
            'one.two.three',
            path_to_module_name('one/two/three.py')
        )

        self.assertEqual(
            'one.two',
            path_to_module_name('one/two/__init__.py')
        )


class AlternativeFeaturesDirTest(unittest.TestCase):
    """Test alternative features directory."""

    def test_alternative_directory(self):
        """Test alternative directory is not a path"""

        with self.assertRaises(StepDiscoveryError):
            os.environ['GHERKIN_FEATURES_DIR_NAME'] = 'my/features'
            FeatureLoader.features_dirname()

        del os.environ['GHERKIN_FEATURES_DIR_NAME']
