"""
Miscellaneous utilities.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sys


def always_str(value):
    """
    Make an str on either Python 2 or Python 3.
    """

    if sys.version_info >= (3, 0):
        return value
    else:
        return value.encode()
