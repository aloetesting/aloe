#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import threading

from aloe.registry import (
    after,
    around,
    before,
    step,
)

world = threading.local()  # pylint:disable=invalid-name
