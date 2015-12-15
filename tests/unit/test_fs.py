"""
Test filesystem-related functions.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import unittest

from aloe.fs import path_to_module_name


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
