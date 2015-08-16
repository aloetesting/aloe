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


class Language(object):
    """
    The keywords for a language

    Implement a language by subclassing the Language class and providing
    the relevant keywords.
    """

    code = None

    def generate_keywords(self, *args):
        """
        Generator yields a list of keywords from the definitions specified
        in the arguments
        """

        for string in args:
            for keyword in self.definitions[string].split(u'|'):
                if keyword.endswith(u'<'):
                    # this language has character words, and we should
                    # treat this as a literal rather than a keyword
                    # (a literal matches the start of a sentence)
                    # minus the <
                    yield Literal(keyword[:-1])
                else:
                    yield Keyword(keyword)

    def build_keywords(self, *args):
        """
        Combine the keywords
        """

        keywords = self.generate_keywords(*args)

        comb = next(keywords)

        for keyword in keywords:
            comb ^= keyword

        return comb

    def __init__(self, code='en'):
        """
        Build a language from definitions.
        """

        self.code = code

        # Compatibility for aliased languages
        key = code
        if code == 'pt-br':
            key = 'pt'

        try:
            self.definitions = I18N_DEFS[key]
        except KeyError:
            raise RuntimeError("Unknown language '%s'" % code)

        # Pyparsing naming
        # pylint:disable=invalid-name
        self.FEATURE = self.build_keywords('feature')
        self.BACKGROUND = self.build_keywords('background')
        self.SCENARIO = self.build_keywords('scenario', 'scenario_outline')
        self.EXAMPLES = self.build_keywords('examples')
        self.STATEMENT = \
            self.build_keywords('given', 'when', 'then', 'and', 'but')
        # pylint:enable=invalid-name

    @property
    def name(self):
        """Language name in English."""
        return self.definitions['name']

    @property
    def native(self):
        """Native language name."""
        return self.definitions['native'].title()

    def __repr__(self):
        return '<Language "%s">' % self.code
