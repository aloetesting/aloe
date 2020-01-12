#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module.
"""

import sys
import threading

from aloe.registry import (
    after,
    around,
    before,
    step,
)
from aloe.runner import Runner

world = threading.local()  # pylint:disable=invalid-name


def main(argv=None):  # pragma: no cover
    """
    Entry point for running Aloe.
    """

    if argv is None:
        argv = sys.argv

    Runner(argv)


if __name__ == '__main__':  # pragma: no cover
    main()
