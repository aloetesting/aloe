#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import time


def main(argv=None):  # pragma: no cover
    """
    Entry point for running Aloe.
    """

    import aloe.plugin
    aloe.plugin.USING_DEPRECATED_RUNNER = True
    sys.stderr.write(
        '**************************************************\n'
        '*        The `aloe` command is deprecated.       *\n'
        '*     Run `nosetests --with-gherkin` instead.    *\n'
        '*          ...sleeping for 3 seconds...          *\n'
        '**************************************************\n'
    )
    time.sleep(3)

    if argv is None:
        argv = sys.argv

    from aloe.runner import Runner
    Runner(argv)
main.USING_DEPRECATED_RUNNER = False

if __name__ == '__main__':  # pragma: no cover
    main()
