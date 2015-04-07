# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) <2014>  Danielle Madeley <danielle@madeley.id.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os.path

from pyparsing import Keyword, Literal


class Language(object):
    """
    The keywords for a language

    Implement a language by subclassing the Language class and providing
    the relevant keywords.
    """

    code = None

    def __init__(self, code='en'):
        for klass in Language.__subclasses__():
            if klass.code == code:
                self.__class__ = klass
                return

        raise RuntimeError("Unknown language '%s'" % code)

    def __repr__(self):
        return '<Language "%s">' % self.code

    @property
    def name(self):
        return self.__class__.__name__

    def print_keywords(self):
        print(u'FEATURE', unicode(self.FEATURE))
        print(u'BACKGROUND', unicode(self.BACKGROUND))
        print(u'SCENARIO', unicode(self.SCENARIO))
        print(u'EXAMPLES', unicode(self.EXAMPLES))
        print(u'STATEMENT', unicode(self.STATEMENT))

    def __implement_me__(self):
        raise NotImplementedError("Language isn't complete")

    FEATURE = BACKGROUND = SCENARIO = EXAMPLES = STATEMENT = \
        property(__implement_me__)


# Load languages from JSON definitions
i18n = os.path.join(os.path.dirname(__file__),
                    'i18n.json')
with open(i18n) as i18n:
    i18n = json.load(i18n)

    for lang, defn in i18n.items():
        name = defn['name']

        def generate_keywords(*args):
            """
            Generator yields a list of keywords from the definitions specified
            in the arguments
            """

            for string in args:
                for keyword in defn[string].split(u'|'):
                    if keyword.endswith(u'<'):
                        # this language has character words, and we should
                        # treat this as a literal rather than a keyword
                        # (a literal matches the start of a sentence)
                        # minus the <
                        yield Literal(keyword[:-1])
                    else:
                        yield Keyword(keyword)

        def build_keywords(*args):
            """
            Combine the keywords
            """

            i_ = generate_keywords(*args)

            comb = next(i_)

            for i_ in i_:
                # take the longest matching keyword
                # (e.g. `Scenario Outline' instead of `Scenario')
                comb ^= i_

            return comb

        locals()[name] = type(str(name), (Language,), {
            'code': lang,
            'native': defn['native'].title(),
            'FEATURE': build_keywords('feature'),
            'BACKGROUND': build_keywords('background'),
            'SCENARIO': build_keywords('scenario', 'scenario_outline'),
            'EXAMPLES': build_keywords('examples'),
            'STATEMENT': build_keywords('given', 'when', 'then', 'and', 'but'),
        })


class PortugueseBrazilian(Portuguese, Language):
    """
    Add pt-br for compatibility
    """

    code = 'pt-br'

    @property
    def name(self):
        return 'Portuguese'
