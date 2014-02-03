# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
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

from pyparsing import Keyword


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

    @classmethod
    def guess_from_string(cls, string):
        # match = re.search(REP.language, string)
        # if match:
        #     instance = cls(match.group(1))
        # else:
        if True:
            instance = cls()

        return instance

    def __implement_me__(self):
        raise NotImplementedError("Language isn't complete")

    FEATURE = BACKGROUND = SCENARIOS = EXAMPLES = STATEMENT = \
        property(__implement_me__)


# Load languages from JSON definitions
i18n = os.path.join(os.path.dirname(__file__),
                    'i18n.json')
with open(i18n) as i18n:
    i18n = json.load(i18n)

    for lang, defn in i18n.iteritems():
        name = defn['name']

        def generate_keywords(*args):
            """
            Generator yields a list of keywords from the definitions specified
            in the arguments
            """

            for string in args:
                for keyword in defn[string].split('|'):
                    if keyword == '*':
                        continue

                    yield Keyword(keyword)

        def build_keywords(*args):
            """
            Combine the keywords
            """

            i_ = generate_keywords(*args)

            comb = next(i_)

            for i_ in i_:
                comb |= i_

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
