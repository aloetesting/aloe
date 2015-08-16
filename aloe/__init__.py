#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import sys
import threading

from aloe.registry import (
    after,
    around,
    before,
    step,
)

world = threading.local()  # pylint:disable=invalid-name


def main(argv=None):  # pragma: no cover
    """
    Entry point for running Aloe.
    """

    if argv is None:
        argv = sys.argv

    from aloe.runner import Runner
    Runner(argv)

if __name__ == '__main__':  # pragma: no cover
    main()
