# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
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
#
"""
A Gherkin parser written using pyparsing
"""

from pyparsing import (CharsNotIn,
                       col,
                       Group,
                       Keyword,
                       lineEnd,
                       lineno,
                       OneOrMore,
                       Optional,
                       ParseException,
                       printables,
                       pythonStyleComment,
                       QuotedString,
                       restOfLine,
                       SkipTo,
                       stringEnd,
                       Suppress,
                       Word,
                       ZeroOrMore)

from lettuce.exceptions import LettuceSyntaxError


class Statement(object):
    """
    A statement
    """

    def __init__(self, s, loc, tokens):

        # statements are made up of a statement sentence + optional data
        # the optional data can either be a table or a multiline string
        try:
            keyword, remainder, data = tokens
        except ValueError:
            keyword, remainder = tokens
            data = None

        self.sentence = keyword + remainder
        self.table = None
        self.multiline = None

        if hasattr(data, 'table'):
            self.table = map(list, data)
        else:
            self.multiline = data

    def __repr__(self):
        r = 'Statement'

        if self.table:
            r += '+Table'
        elif self.multiline:
            r += '+Multiline'

        r += '<%s>' % self.statement

        return r

    @property
    def keys(self):
        """
        Return the first row of a table if this statement contains one
        """
        return tuple(self.table[0])

    @property
    def hashes(self):
        keys = self.keys

        return [
            dict(zip(keys, row))
            for row in self.table[1:]
        ]


class Block(object):
    """
    A generic block, e.g. Feature:, Scenario:

    Blocks contain a number of statements
    """

    def __init__(self, tokens):
        self.statements = []

    @classmethod
    def add_statements(cls, tokens):
        """
        Consume the statements to add to this block
        """

        token = tokens[0]

        self = token.node
        self.steps = list(token.statements)

        assert all(isinstance(statement, Statement)
                   for statement in self.steps)

        return self


class TaggedBlock(Block):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, s, loc, tokens):
        super(TaggedBlock, self).__init__(tokens)

        token = tokens[0]

        self._tags = list(token.tags)
        self.name = token.name.strip()

        if self.name == '':
            raise LettuceSyntaxError(
                None,
                "{line}:{col} {klass} must have a name".format(
                    line=lineno(loc, s),
                    col=col(loc, s),
                    klass=self.__class__.__name__))

    def __unicode__(self):
        return '<{klass}: "{name}">'.format(
            # FIXME: use self.language
            klass=self.__class__.__name__,
            name=self.name)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    @property
    def tags(self):
        return self._tags


class Background(Block):
    pass


class Scenario(TaggedBlock):
    @classmethod
    def add_statements(cls, tokens):
        token = tokens[0]

        self = super(Scenario, cls).add_statements(tokens)

        self.examples = token.examples

        return self

    @property
    def tags(self):
        return self._tags + self.feature.tags


class Feature(TaggedBlock):
    @classmethod
    def add_blocks(cls, tokens):
        """
        Add the background and other blocks to the feature
        """

        token = tokens[0]

        self = token.node
        self.description = '\n'.join(line.strip()
                                     for line
                                     in token.description[0].split('\n'))\
            .strip()
        self.background = token.background \
            if isinstance(token.background, Background) else None
        self.scenarios = list(token.scenarios)

        # add the back references
        if self.background:
            self.background.feature = self

        for scenario in self.scenarios:
            scenario.feature = self

        return self


"""
End of Line
"""
EOL = Suppress(lineEnd)

"""
@tag
"""
TAG = Suppress('@') + Word(printables)

"""
A table
"""
TABLE_ROW = Suppress('|') + OneOrMore(CharsNotIn('|\n') + Suppress('|')) + EOL
TABLE_ROW.setParseAction(lambda tokens: [v.strip() for v in tokens])
TABLE = Group(OneOrMore(Group(TABLE_ROW)))('table')

"""
Multiline string
"""
MULTILINE = QuotedString('"""', multiline=True)

"""
Statement
"""
BLOCK_DESC = Suppress('*') + restOfLine

STATEMENT_KEYWORD = \
    Keyword('Given') | \
    Keyword('When') | \
    Keyword('Then') | \
    Keyword('And')


STATEMENT = \
    STATEMENT_KEYWORD + \
    restOfLine + \
    Optional(TABLE | MULTILINE)
STATEMENT.setParseAction(Statement)

STATEMENTS = Group(ZeroOrMore(STATEMENT))

"""
Background:
"""
BACKGROUND_DEFN = \
    Suppress(Keyword('Background') + ':' + EOL)
BACKGROUND_DEFN.setParseAction(Background)

BACKGROUND = Group(
    BACKGROUND_DEFN('node') +
    STATEMENTS('statements')
)
BACKGROUND.setParseAction(Background.add_statements)

"""
Scenario: description
"""
SCENARIO_DEFN = Group(
    Group(ZeroOrMore(TAG))('tags') +
    Suppress((Keyword('Scenario') + Optional(Keyword('Outline'))) +
             ':') +
    restOfLine('name')
)
SCENARIO_DEFN.setParseAction(Scenario)

SCENARIO = Group(
    SCENARIO_DEFN('node') +
    STATEMENTS('statements') +
    Optional(Suppress(Keyword('Examples') + ':') + EOL + TABLE('examples'))
)
SCENARIO.setParseAction(Scenario.add_statements)

"""
Feature: description
"""
FEATURE_DEFN = Group(
    Group(ZeroOrMore(TAG))('tags') +
    Suppress(Keyword('Feature') + ':') +
    restOfLine('name')
)
FEATURE_DEFN.setParseAction(Feature)


"""
Complete feature file definition
"""
FEATURE = Group(
    FEATURE_DEFN('node') +
    Group(SkipTo(BACKGROUND | SCENARIO))('description') +
    Optional(BACKGROUND('background')) +
    Group(OneOrMore(SCENARIO))('scenarios') +
    stringEnd)
FEATURE.ignore(pythonStyleComment)
FEATURE.setParseAction(Feature.add_blocks)


def from_string(cls, string):
    """
    Parse a Feature object from a string
    """

    try:
        tokens = FEATURE.parseString(string)
        return tokens[0]
    except ParseException as e:
        print "Syntax Error, line", e.lineno
        print e.line
        print " " * (e.column - 1) + "^"

        print e.parserElement
        print e.pstr
        raise

Feature.from_string = classmethod(from_string)
