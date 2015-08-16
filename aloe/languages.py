# -*- coding: utf-8 -*-
"""
Gherkin language definitions
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import open
# pylint:enable=redefined-builtin
from future import standard_library
standard_library.install_aliases()
import json
import os.path

from pyparsing import Keyword, Literal


# Load languages from JSON definitions
I18N_FILE = os.path.join(os.path.dirname(__file__), 'i18n.json')
with open(I18N_FILE) as i18n:
    I18N_DEFS = json.load(i18n)


def Language(l='en'):
    return l
