"""
Steps for features used in unit tests.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from aloe import step


@step(r'I do nothing')
def trivial_step(self):  # pylint:disable=unused-argument
    """Trivial passing step."""
    pass


@step(r'I fail')
def failing_step(self):  # pylint:disable=unused-argument
    """Trivial failing step."""
    raise AssertionError("This step is meant to fail.")
