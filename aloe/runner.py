"""
Unittest runner working with Gherkin tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import super
# pylint:enable=redefined-builtin

import unittest

from aloe.result import AloeTestResult


class GherkinRunner(unittest.runner.TextTestRunner):
    """
    A test runner with Aloe result class.
    """

    def __init__(self, *args, **kwargs):
        """Remember the extra arguments."""
        self.force_color = kwargs.pop('force_color')
        super().__init__(*args, **kwargs)

    def resultclass(self, *args, **kwargs):  # pylint:disable=method-hidden
        """Construct an overridden result with extra arguments."""
        kwargs['force_color'] = self.force_color
        return AloeTestResult(*args, **kwargs)
